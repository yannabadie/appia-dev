# src/jarvys_dev/tools/memory.py
from __future__ import annotations
import os, uuid, typing as _t
from openai import OpenAI
from supabase import create_client

SUPABASE_URL  = os.environ["SUPABASE_URL"]
SUPABASE_KEY  = os.environ["SUPABASE_KEY"]
_openai_key   = os.environ["OPENAI_API_KEY"]

_sb   = create_client(SUPABASE_URL, SUPABASE_KEY)
_ocl  = OpenAI(api_key=_openai_key)

_DIM  = 1536       # modèle text‑embedding‑3‑small

def _embed(text: str) -> list[float]:
    resp = _ocl.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8192]          # limite contextuelle
    )
    return resp.data[0].embedding

# ------------------------------------------------------------------ public
def upsert_embedding(content: str, doc_id: str|None=None) -> str:
    """Insert / update un document et son embedding.  
       Retourne l’UUID."""
    emb = _embed(content)
    doc_id = doc_id or str(uuid.uuid4())
    _sb.table("documents").upsert(
        {"id": doc_id, "content": content, "embedding": emb},
        on_conflict="id"
    ).execute()
    return doc_id

def memory_search(query: str, k: int = 5) -> list[str]:
    """Recherche sémantique ; renvoie les contenus les + proches."""
    q_emb = _embed(query)
    res = _sb.rpc(
        "match_documents",  # fonction SQL créée ci‑dessous
        {"query_embedding": q_emb, "match_count": k}
    ).execute()
    return [r["content"] for r in res.data]
