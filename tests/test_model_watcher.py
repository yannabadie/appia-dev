import json

from jarvys_dev import model_watcher


def test_check_for_new_models(tmp_path, monkeypatch):
    cfg = {"openai": "a", "gemini": "b"}
    cfg_path = tmp_path / "model_config.json"
    cfg_path.write_text(json.dumps(cfg))
    monkeypatch.setattr(model_watcher, "CONFIG_PATH", cfg_path)

    monkeypatch.setattr(
        model_watcher,
        "_fetch_openai_models",
        lambda: ["a", "c"],
    )
    monkeypatch.setattr(
        model_watcher,
        "_fetch_gemini_models",
        lambda: ["b", "d"],
    )
    monkeypatch.setattr(model_watcher, "_fetch_anthropic_models", lambda: [])

    created = []

    def dummy_issue(
        title: str,
        body: str = "",
        labels=None,
        repo_fullname=None,
    ):
        created.append((title, body))
        return "url"

    monkeypatch.setattr(model_watcher, "github_create_issue", dummy_issue)

    changed = model_watcher.check_for_new_models()
    assert changed is True
    data = json.loads(cfg_path.read_text())
    assert data["openai"] == "c"
    assert data["gemini"] == "d"
    assert created
