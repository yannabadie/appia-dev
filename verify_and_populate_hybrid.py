"""Verify API access for local and cloud contexts and populate Supabase."""

from __future__ import annotations

import json
import logging
import os

import google.generativeai as genai
from openai import OpenAI
from supabase import Client, create_client

# OpenAI embedding models accept a maximum of 8192 tokens. Truncate any
# longer text to ensure the API does not fail.
EMBEDDING_SLICE_LIMIT = 8192

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

USER_CONTEXT = {
    "psychological_profile": {
        "iq": 130,
        "anxiety": "mild",
        "depression": "none",
        "sleep": "good",
    },
    "medical": {"epilepsy": True, "medications": ["lamotrigine"]},
    "professional": [
        "Azure Cloud",
        "Cybersecurity",
        "Microsoft Intune",
        "Microsoft Defender",
        "Microsoft Purview",
    ],
    "personal_interests": ["hiking", "bodybuilding", "reading"],
    "ethical_ai_goals": "Develop responsible AI for society",
}


# ---------------------------- helpers


def _embed_text(client: OpenAI, text: str) -> list[float]:
    resp = client.embeddings.create(
        model="text-embedding-3-large",
        input=text[:EMBEDDING_SLICE_LIMIT],
    )
    return resp.data[0].embedding


def _ensure_db(sb: Client) -> None:
    sql = """
    create extension if not exists vector;
    create table if not exists memory_vectors (
        id uuid primary key default gen_random_uuid(),
        content text,
        embedding vector(3072),
        metadata jsonb
    );
    create table if not exists user_preferences (
        id uuid primary key default gen_random_uuid(),
        user_metadata jsonb
    );
    create table if not exists logs (
        id uuid primary key default gen_random_uuid(),
        activity text,
        api_cost float8,
        created_at timestamptz default now()
    );
    """
    try:
        sb.rpc("sql", {"query": sql}).execute()
    except Exception as exc:  # pragma: no cover - optional server function
        logging.warning("Table setup failed: %s", exc)
    try:
        buckets = [b["name"] for b in sb.storage.list_buckets().data]
        for name in ("documents", "archives"):
            if name not in buckets:
                sb.storage.create_bucket(name)
    except Exception as exc:  # pragma: no cover - network failures
        logging.warning("Bucket setup failed: %s", exc)


def _populate(sb: Client, ocl: OpenAI) -> None:
    content = json.dumps(USER_CONTEXT, ensure_ascii=False)
    try:
        _embed_text(ocl, content)
        logging.info("Embedding created successfully")
    except Exception as exc:  # pragma: no cover - network failures
        logging.error("Embedding failed: %s", exc)
        return
    
    # Note: Avec la clé 'anon', nous ne pouvons pas insérer de données
    # car Row Level Security (RLS) est activé. Ceci est normal et sécurisé.
    logging.info(
        "User context processed (insertion skipped due to RLS with anon key)"
    )
    logging.info(
        "To enable data insertion, use service_role key instead of anon key"
    )


# ---------------------------- verification per context


def verify_context(prefix: str) -> None:
    logging.info("--- Verifying %s environment ---", prefix)
    ok = True

    openai_key = os.getenv(f"OPENAI_API_KEY_{prefix}")
    gemini_key = os.getenv(f"GEMINI_API_KEY_{prefix}")
    supabase_url = os.getenv(f"SUPABASE_URL_{prefix}")
    supabase_key = os.getenv(f"SUPABASE_KEY_{prefix}")

    if not all([openai_key, gemini_key, supabase_url, supabase_key]):
        logging.error("Missing environment variables for %s", prefix)
        return

    # OpenAI
    try:
        ocl = OpenAI(api_key=openai_key)
        ocl.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "ping"}],
        )
        logging.info("OpenAI accessible (%s)", prefix)
    except Exception as exc:  # pragma: no cover - network failures
        logging.error("OpenAI check failed (%s): %s", prefix, exc)
        ok = False
        ocl = None

    # Gemini
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        model.generate_content("ping")
        logging.info("Gemini accessible (%s)", prefix)
    except Exception as exc:  # pragma: no cover - network failures
        logging.error("Gemini check failed (%s): %s", prefix, exc)
        ok = False

    # Supabase
    try:
        sb = create_client(supabase_url, supabase_key)
        # Utiliser la table documents qui existe au lieu de logs
        sb.table("documents").select("*").limit(1).execute()
        logging.info("Supabase accessible (%s)", prefix)
    except Exception as exc:  # pragma: no cover - network failures
        logging.error("Supabase check failed (%s): %s", prefix, exc)
        ok = False
        sb = None

    if ok and sb and ocl:
        _ensure_db(sb)
        _populate(sb, ocl)
        logging.info("%s verification complete", prefix)
    else:
        logging.warning(
            "%s verification incomplete due to earlier errors",
            prefix,
        )


def main() -> None:
    for env in ("LOCAL", "CLOUD"):
        verify_context(env)


if __name__ == "__main__":
    main()
