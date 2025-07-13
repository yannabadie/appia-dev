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

from .intelligent_orchestrator import get_orchestrator

CONFIG_PATH = Path(__file__).with_name("model_config.json")
DEFAULT_MODELS = {
    "openai": "gpt-4o",  # Modèle OpenAI le plus performant
    "anthropic": "claude-sonnet-4-20250514",  # Claude 4 Sonnet (2025)
    "gemini": "gemini-2.5-pro",  # Gemini 2.5 Pro avec thinking
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

        # Orchestrateur intelligent
        self.orchestrator = get_orchestrator()

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

        # Load model capabilities from JSON file if present
        self.model_capabilities = self._load_model_capabilities()

        self.benchmarks: list[Benchmark] = []

    # ---------------------------- helpers
    def _load_model_capabilities(self) -> dict:
        """Load model capabilities from JSON file."""
        capabilities_path = os.path.join(
            os.path.dirname(__file__), "model_capabilities.json"
        )
        try:
            with open(capabilities_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

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
    def generate(self, prompt: str, *, task_type: str = "auto") -> str:
        """Generate a completion using the optimal model selected by AI orchestrator."""

        # Analyse intelligente de la tâche
        task_analysis = self.orchestrator.analyze_task(prompt, task_type)

        # Sélection du modèle optimal
        optimal_model, model_info, confidence = (
            self.orchestrator.select_optimal_model(task_analysis)
        )

        logger.info(
            f"🎯 Tâche: {task_analysis.task_type}, Modèle: {optimal_model}, "
            f"Confiance: {confidence:.2f}"
        )

        # Exécution avec le modèle sélectionné
        start = time.perf_counter()
        _result = None
        success = False

        try:
            # Déterminer le provider du modèle optimal
            provider = model_info.provider

            if provider == "openai" and self.openai_client:
                _result = self._execute_openai(optimal_model, prompt)
                success = True

            elif provider == "gemini" and self.gemini_available:
                _result = self._execute_gemini(optimal_model, prompt)
                success = True

            elif provider == "anthropic" and self.anthropic_client:
                _result = self._execute_anthropic(optimal_model, prompt)
                success = True

            else:
                # Fallback vers ordre par défaut si modèle optimal indisponible
                logger.warning(
                    f"⚠️ Modèle optimal {optimal_model} indisponible, fallback"
                )
                _result = self._fallback_generation(
                    prompt, task_analysis.task_type
                )
                success = True

            # Enregistrer les performances
            end_time = time.perf_counter()
            latency = end_time - start

            # Estimer le coût (approximatif)
            estimated_cost = model_info.cost_per_1k_tokens * (
                len(prompt.split()) / 1000
            )

            # Enregistrer pour apprentissage
            self.orchestrator.record_performance(
                optimal_model,
                task_analysis.task_type,
                1.0 if success else 0.0,
                latency,
                estimated_cost,
            )

            self._record_bench(optimal_model, start, prompt)

            return _result

        except Exception as exc:
            logger.error(
                f"❌ Erreur avec modèle optimal {optimal_model}: {exc}"
            )

            # Enregistrer l'échec
            self.orchestrator.record_performance(
                optimal_model,
                task_analysis.task_type,
                0.0,
                time.perf_counter() - start,
                0.0,
            )

            # Fallback vers autre modèle
            return self._fallback_generation(prompt, task_analysis.task_type)

    def _execute_openai(self, model: str, prompt: str) -> str:
        """Exécute une requête OpenAI."""
        resp = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000,
        )
        return resp.choices[0].message.content

    def _execute_gemini(self, model: str, prompt: str) -> str:
        """Exécute une requête Gemini."""
        genai_model = genai.GenerativeModel(model)
        resp = genai_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7, max_output_tokens=4000
            ),
        )
        return getattr(resp, "text", str(resp))

    def _execute_anthropic(self, model: str, prompt: str) -> str:
        """Exécute une requête Anthropic."""
        resp = self.anthropic_client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.7,
        )
        part = resp.content[0]
        return part.text if hasattr(part, "text") else str(part)

    def _fallback_generation(self, prompt: str, task_type: str) -> str:
        """Génération de fallback si modèle optimal indisponible."""
        models = self.model_names
        config = {
            "multimodal": {
                "order": ["gemini", "anthropic", "openai"],
                "models": {
                    "gemini": models["gemini"],  # gemini-2.5-pro
                    "anthropic": models[
                        "anthropic"
                    ],  # claude-sonnet-4-20250514
                    "openai": models["openai"],  # gpt-4o
                },
            },
            "reasoning": {
                "order": ["anthropic", "openai", "gemini"],
                "models": {
                    "anthropic": models[
                        "anthropic"
                    ],  # claude-sonnet-4-20250514
                    "openai": models["openai"],  # gpt-4o
                    "gemini": models["gemini"],  # gemini-2.5-pro
                },
            },
            "creativity": {
                "order": ["anthropic", "gemini", "openai"],
                "models": {
                    "anthropic": models[
                        "anthropic"
                    ],  # claude-sonnet-4-20250514
                    "gemini": models["gemini"],  # gemini-2.5-pro
                    "openai": models["openai"],  # gpt-4o
                },
            },
            "coding": {
                "order": ["openai", "anthropic", "gemini"],
                "models": {
                    "openai": models["openai"],  # gpt-4o
                    "anthropic": models[
                        "anthropic"
                    ],  # claude-sonnet-4-20250514
                    "gemini": models["gemini"],  # gemini-2.5-pro
                },
            },
            "mathematical": {
                "order": ["openai"],
                "models": {
                    "openai": "o1-preview"
                },  # Spécialisé pour le raisonnement
            },
        }

        task_cfg = config.get(task_type, config["reasoning"])
        order = task_cfg["order"]
        model_map = task_cfg["models"]

        for provider in order:
            start = time.perf_counter()
            try:
                if provider == "openai" and self.openai_client:
                    _result = self._execute_openai(model_map[provider], prompt)
                    self._record_bench(model_map[provider], start, prompt)
                    return _result

                if provider == "gemini" and self.gemini_available:
                    _result = self._execute_gemini(model_map[provider], prompt)
                    self._record_bench(model_map[provider], start, prompt)
                    return _result

                if provider == "anthropic" and self.anthropic_client:
                    _result = self._execute_anthropic(
                        model_map[provider], prompt
                    )
                    self._record_bench(model_map[provider], start, prompt)
                    return _result

            except Exception as exc:  # pragma: no cover - network failures
                logger.warning("%s failed: %s", provider, exc)

        raise RuntimeError("No available model for generation")


__all__ = ["MultiModelRouter", "Benchmark"]
