import types
from unittest import mock


class DummyResp:
    def __init__(self, text="ok"):
        self.text = text
        self.choices = [mock.Mock(message=mock.Mock(content=text))]
        self.content = [mock.Mock(text=text)]


@mock.patch.dict("os.environ", {"OPENAI_API_KEY": "k"})
def test_router_openai(monkeypatch):
    dummy = mock.Mock()
    dummy.chat.completions.create.return_value = DummyResp("openai")
    monkeypatch.setattr(
        "jarvys_dev.multi_model_router.OpenAI", lambda api_key=None: dummy
    )
    from jarvys_dev.multi_model_router import MultiModelRouter

    router = MultiModelRouter()
    out = router.generate("hi", task_type="reasoning")
    assert out == "openai"
    dummy.chat.completions.create.assert_called_once()


def test_router_fallback_to_gemini(monkeypatch):
    dummy_model = mock.Mock()
    dummy_model.generate_content.return_value = DummyResp("gemini")
    dummy_module = types.SimpleNamespace(
        configure=lambda api_key=None: None,
        GenerativeModel=lambda name: dummy_model,
    )
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from jarvys_dev import multi_model_router as mmr

    monkeypatch.setattr(mmr, "genai", dummy_module, raising=False)
    from jarvys_dev.multi_model_router import MultiModelRouter

    router = MultiModelRouter()
    out = router.generate("hi", task_type="multimodal")
    assert out == "gemini"
    dummy_model.generate_content.assert_called_once()
