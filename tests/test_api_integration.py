import os

import pytest
import requests
from supabase import create_client

DEFAULT_TIMEOUT_SECONDS = 15


def requires_env(*names: str) -> pytest.MarkDecorator:
    missing = [n for n in names if not os.getenv(n)]
    reason = ", ".join(missing) + " missing"
    return pytest.mark.skipif(bool(missing), reason=reason)


integration = pytest.mark.integration


@integration
@requires_env("OPENAI_API_KEY")
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
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    data = resp.json()
    assert "choices" in data


@integration
@requires_env("GEMINI_API_KEY")
def test_gemini_generation():
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-pro:generateContent"
        f"?key={os.environ['GEMINI_API_KEY']}"
    )
    resp = requests.post(
        url,
        json={"contents": [{"parts": [{"text": "ping"}]}]},
        timeout=DEFAULT_TIMEOUT_SECONDS,
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


@integration
@requires_env("SUPABASE_URL", "SUPABASE_KEY")
def test_supabase_select():
    client = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )
    resp = client.table("documents").select("*").limit(1).execute()
    assert resp.data
