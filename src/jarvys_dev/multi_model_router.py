"""Router for multiple LLM providers.

This module selects the best model depending on the ``task_type`` and
available API keys. It also implements a simple fallback strategy and
basic benchmarking (latency, prompt size for cost approximation).
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # optional dependency
    import google.generativeai as genai
except Exception:  # pragma: no cover - package optional
    genai = None

try:  # optional dependency
    from anthropic import Anthropic
except Exception:  # pragma: no cover - package optional
    Anthropic = None  # type: ignore

from openai import OpenAI

CONFIG_PATH = Path(__file__).with_name("model_config.json")
DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-opus-20240229",
    "gemini": "models/gemini-1.5-pro",
}


def _load_models() -> dict[str, str]:
    models = DEFAULT_MODELS.copy()
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as fh:
                data = json.load(fh)
            clean = {k: v for k, v in data.items() if isinstance(v, str)}
            models.update(clean)
        except Exception as exc:  # pragma: no cover - config errors
            logger.warning("Failed to read %s: %s", CONFIG_PATH, exc)
    return models


logger = logging.getLogger(__name__)


@dataclass
class Benchmark:
    model: str
    latency: float
    cost: float | None = None


class MultiModelRouter:
    """Route prompts to the optimal LLM."""

    def __init__(self) -> None:
        self.model_names = _load_models()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        self.openai_client: OpenAI | None = None
        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)

        self.gemini_available = False
        if genai and self.gemini_key:
            try:  # pragma: no cover - network failures ignored
                genai.configure(api_key=self.gemini_key)
                self.gemini_available = True
            except Exception as exc:  # pragma: no cover - package errors
                logger.warning("Gemini init failed: %s", exc)

        self.anthropic_client: Any | None = None
        if Anthropic and self.anthropic_key:
            try:  # pragma: no cover
                self.anthropic_client = Anthropic(api_key=self.anthropic_key)
            except Exception as exc:  # pragma: no cover - package errors
                logger.warning("Anthropic init failed: %s", exc)

        self.benchmarks: list[Benchmark] = []

    # ---------------------------- helpers
    def _record_bench(self, model: str, start: float, prompt: str) -> None:
        latency = time.perf_counter() - start
        cost = len(prompt) / 1000  # crude proxy
        self.benchmarks.append(
            Benchmark(
                model=model,
                latency=latency,
                cost=cost,
            )
        )

    # ------------------------------------------------------------------ public
    def generate(self, prompt: str, *, task_type: str = "reasoning") -> str:
        """Generate a completion using the best available model."""
        if task_type == "multimodal":
            order = ["gemini", "openai", "anthropic"]
        else:  # reasoning or creativity
            order = ["openai", "anthropic", "gemini"]

        models = self.model_names

        for provider in order:
            start = time.perf_counter()
            try:
                if provider == "openai" and self.openai_client:
                    resp = self.openai_client.chat.completions.create(
                        model=models[provider],
                        messages=[{"role": "user", "content": prompt}],
                    )
                    self._record_bench(models[provider], start, prompt)
                    return resp.choices[0].message.content

                if provider == "gemini" and self.gemini_available:
                    model = genai.GenerativeModel(models[provider])
                    resp = model.generate_content(prompt)
                    self._record_bench(models[provider], start, prompt)
                    return getattr(resp, "text", str(resp))

                if provider == "anthropic" and self.anthropic_client:
                    resp = self.anthropic_client.messages.create(
                        model=models[provider],
                        messages=[{"role": "user", "content": prompt}],
                    )
                    self._record_bench(models[provider], start, prompt)
                    part = resp.content[0]
                    return part.text if hasattr(part, "text") else str(part)
            except Exception as exc:  # pragma: no cover - network failures
                logger.warning("%s failed: %s", provider, exc)

        raise RuntimeError("No available model for generation")


__all__ = ["MultiModelRouter", "Benchmark"]
