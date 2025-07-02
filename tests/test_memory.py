# tests/test_memory.py
import os, pytest
from jarvys_dev.tools import memory

pytest.skip("Env vars Supabase manquantes",
            allow_module_level=not all(os.getenv(k)
                                       for k in ("SUPABASE_URL","SUPABASE_KEY","OPENAI_API_KEY")))

def test_roundtrip():
    txt = "Hello JARVYS memory!"
    doc_id = memory.upsert_embedding(txt)
    results = memory.memory_search("Hello")
    assert txt in results
