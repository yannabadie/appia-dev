import os

import pytest
import requests
from supabase import create_client


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY missing",
)
def test_openai_completion():
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "ping"}],
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    assert "choices" in data


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY missing",
)
def test_gemini_generation():
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-pro:generateContent"
        f"?key={os.environ['GEMINI_API_KEY']}"
    )
    resp = requests.post(
        url,
        json={"contents": [{"parts": [{"text": "ping"}]}]},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text")
    )
    assert text is not None


@pytest.mark.skipif(
    not (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")),
    reason="Supabase credentials missing",
)
def test_supabase_select():
    client = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )
    resp = client.table("documents").select("*").limit(1).execute()
    assert resp.data
