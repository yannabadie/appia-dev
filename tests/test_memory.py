# tests/test_memory.py
import os

import pytest

secrets_ok = all(
    os.getenv(k) for k in ("SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY")
)

if not secrets_ok:
    pytest.skip(
        "Secrets Supabase / OpenAI manquants.",
        allow_module_level=True,
    )

from jarvys_dev.tools import memory


def test_upsert_and_search_roundtrip():
    txt = "JARVYS loves vector databases!"
    doc_id = memory.upsert_embedding(txt)
    assert isinstance(doc_id, str)

    hits = memory.memory_search("vector databases", k=3)
    assert any(txt in h for h in hits)


def test_load_config_initializes_clients(monkeypatch):
    memory._sb = None
    memory._ocl = None
    monkeypatch.setenv("SUPABASE_URL", "https://db.example.com")
    monkeypatch.setenv("SUPABASE_KEY", "supakey")
    monkeypatch.setenv("OPENAI_API_KEY", "openkey")

    dummy_sb = object()
    dummy_ocl = object()
    monkeypatch.setattr(memory, "create_client", lambda url, key: dummy_sb)
    monkeypatch.setattr(memory, "OpenAI", lambda api_key=None: dummy_ocl)

    memory._load_config()
    assert memory._sb is dummy_sb
    assert memory._ocl is dummy_ocl
