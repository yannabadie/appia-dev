# tests/test_memory.py
import os, pytest
from jarvys_dev.tools import memory

secrets_ok = all(os.getenv(k) for k in ("SUPABASE_URL","SUPABASE_KEY","OPENAI_API_KEY"))

pytest.skip("Secrets Supabase / OpenAI manquants.",
            allow_module_level=True) if not secrets_ok else None


def test_upsert_and_search_roundtrip():
    txt = "JARVYS loves vector databases!"
    doc_id = memory.upsert_embedding(txt)
    assert isinstance(doc_id, str)

    hits = memory.memory_search("vector databases", k=3)
    assert any(txt in h for h in hits)
