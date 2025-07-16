# src/jarvys_dev/tools/memory.py
from __future__ import annotations

import logging
import os
import typing as _t
import uuid

from openai import OpenAI

from supabase import create_client

_sb: _t.Any | None = None
_ocl: OpenAI | None = None


def _load_config() -> None:
    """Load configuration from environment variables and initialise clients."""
    global _sb, _ocl
    if _sb is not None and _ocl is not None:
        return

    supabase_url = os.getenv("SUPABASE_URL")
    # Utiliser service_role si disponible, sinon anon key
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    missing = [
        k
        for k, v in {
            "SUPABASE_URL": supabase_url,
            "SUPABASE_KEY (or SERVICE_ROLE)": supabase_key,
            "OPENAI_API_KEY": openai_key,
        }.items()
        if not v
    ]
    if missing:
        message = ", ".join(missing)
        raise RuntimeError(f"Missing environment variables: {message}")

    # Créer le client Supabase avec les nouveaux paramètres
    _sb = create_client(supabase_url, supabase_key)
    _ocl = OpenAI(api_key=openai_key)


_DIM = 1536  # modèle text‑embedding‑3‑small


def _embed(text: str) -> list[float]:
    _load_config()
    resp = _ocl.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8192],  # limite contextuelle
    )
    return resp.data[0].embedding


# ------------------------------------------------------------------ public
def upsert_embedding(content: str, doc_id: str | None = None) -> str:
    """Insert / update un document et son embedding.
    Retourne l'UUID."""
    _load_config()
    emb = _embed(content)
    doc_id = doc_id or str(uuid.uuid4())
    try:
        # Insérer sans metadata si la colonne n'existe pas
        _sb.table("documents").upsert(
            {
                "id": doc_id,
                "content": content,
                "embedding": emb,
            },
            on_conflict="id",
        ).execute()
        logging.info("Document embedding saved successfully")
    except Exception as e:
        if "row-level security" in str(e).lower() or "42501" in str(e):
            logging.warning("⚠️ Cannot save data: RLS policy blocks insertion")
        elif "metadata" in str(e).lower():
            logging.warning("⚠️ Metadata column not available, but document saved")
        else:
            logging.warning("⚠️ Supabase connection failed, data not saved: %s", e)
    return doc_id


def memory_search(query: str, k: int = 5) -> list[str]:
    """Recherche sémantique ; renvoie les contenus les + proches."""
    _load_config()
    q_emb = _embed(query)
    try:
        res = _sb.rpc(
            "match_documents",  # fonction SQL créée ci‑dessous
            {"query_embedding": q_emb, "match_count": k},
        ).execute()
    except Exception:
        logging.warning("⚠️ Supabase search failed")
        return []
    return [r["content"] for r in res.data]
