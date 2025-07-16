from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Iterable

import requests
from openai import OpenAI

from .tools.github_tools import github_create_issue

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).with_name("model_config.json")


def _load_config() -> dict[str, str]:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as fh:
            return json.load(fh)
    return {}


def _save_config(cfg: dict[str, str]) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")


def _fetch_openai_models() -> list[str]:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return []
    client = OpenAI(api_key=key)
    return [m.id for m in client.models.list().data]


def _fetch_anthropic_models() -> list[str]:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return []
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    resp = requests.get(
        "https://api.anthropic.com/v1/models", headers=headers, timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    models = data.get("models") or data.get("data", [])
    return [m.get("name") or m.get("id") for m in models]


def _fetch_gemini_models() -> list[str]:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return []
    url = "https://generativelanguage.googleapis.com/v1/models"
    resp = requests.get(f"{url}?key={key}", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    models = data.get("models") or data.get("data", [])
    return [m.get("name") for m in models if m.get("name")]


def _detect_new(
    current: dict[str, str], provider: str, avail: Iterable[str]
) -> str | None:
    avail = sorted(avail)
    if not avail:
        return None
    latest = avail[-1]
    if current.get(provider) != latest:
        current[provider] = latest
        return latest
    return None


def check_for_new_models() -> bool:
    cfg = _load_config()
    updates: dict[str, str] = {}
    if new := _detect_new(cfg, "openai", _fetch_openai_models()):
        updates["openai"] = new
    if new := _detect_new(cfg, "anthropic", _fetch_anthropic_models()):
        updates["anthropic"] = new
    if new := _detect_new(cfg, "gemini", _fetch_gemini_models()):
        updates["gemini"] = new

    if updates:
        _save_config(cfg)
        body = "Updated model config = {}:\n```json\n"
        body += json.dumps(updates, indent=2)
        body += "\n```"
        try:
            github_create_issue(title="New models detected", body=body)
        except Exception as exc:  # pragma: no cover - network
            logger = logging.getLogger(__name__).warning(
                "Issue creation failed: %s", exc
            )
        return True
    return False


def main() -> None:
    changed = check_for_new_models()
    print("updated" if changed else "no change")


if __name__ == "__main__":  # pragma: no cover
    main()
