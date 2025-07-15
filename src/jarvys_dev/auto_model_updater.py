"""
Module de mise à jour automatique des modèles LLM.
Surveille Hugging Face, OpenAI, Anthropic et Google pour les nouveaux modèles.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

from .tools.memory_infinite import get_memory

logger = logging.getLogger(__name__)


@dataclass
class ModelUpdate:
    """Information sur une mise à jour de modèle."""

    model_name: str
    provider: str
    version: str
    release_date: str
    capabilities: List[str]
    performance_improvements: List[str]
    breaking_changes: List[str]
    recommended_use_cases: List[str]


class AutoModelUpdater:
    """Système de mise à jour automatique des modèles."""

    def __init__(self):
        self.memory = get_memory("JARVYS_DEV", "model_updates")
        self.last_check = None
        self.available_updates = []

        # APIs endpoints
        self.endpoints = {
            "huggingface": "https://huggingface.co/api/models",
            "openai": "https://api.openai.com/v1/models",
            "anthropic_blog": "https://www.anthropic.com/api/blog",
            # Hypothétique
            "google_ai": "https://generativelanguage.googleapis.com/v1beta/models",
        }

        logger.info("🔄 Auto-updater des modèles initialisé")

    def check_for_updates(self) -> List[ModelUpdate]:
        """Vérifie tous les providers pour de nouveaux modèles."""

        logger.info("🔍 Vérification des mises à jour de modèles...")
        updates = []

        # Vérifier chaque provider
        try:
            # 1. Hugging Face (source principale)
            hf_updates = self._check_huggingface_updates()
            updates.extend(hf_updates)

            # 2. OpenAI
            openai_updates = self._check_openai_updates()
            updates.extend(openai_updates)

            # 3. Google/Gemini
            gemini_updates = self._check_gemini_updates()
            updates.extend(gemini_updates)

            # 4. Anthropic (surveillance manuelle pour l'instant)
            anthropic_updates = self._check_anthropic_updates()
            updates.extend(anthropic_updates)

            self.available_updates = updates
            self.last_check = datetime.now().isoformat()

            # Mémoriser les découvertes
            if updates:
                update_info = (
                    "Nouvelles mises à jour de modèles détectées:"
                    "{len(updates)} "
                    "modèles - "
                    + ", ".join(
                        [f"{u.provider}/{u.model_name}" for u in updates[:3]]
                    )
                )
                self.memory.memorize(
                    update_info,
                    memory_type="knowledge",
                    importance_score=0.8,
                    tags=["model_updates", "technology", "ai"],
                    metadata={
                        "updates_count": len(updates),
                        "check_date": self.last_check,
                    },
                )

            logger.info(
                f"✅ Vérification terminée: {len(updates)} mises à jour"
                "trouvées"
            )
            return updates

        except Exception as e:
            logger.error(f"❌ Erreur vérification mises à jour: {e}")
            return []

    def _check_huggingface_updates(self) -> List[ModelUpdate]:
        """Vérifie les nouveaux modèles sur Hugging Face."""
        updates = []

        try:
            # Modèles tendance récents
            params = {
                "sort": "trending",
                "filter": "text-generation",
                "limit": 50,
            }

            _response = requests.get(
                self.endpoints["huggingface"], params=params, timeout=15
            )

            if _response.status_code == 200:
                models = _response.json()

                # Filtrer les modèles intéressants (derniers 30 jours)
                cutoff_date = datetime.now() - timedelta(days=30)

                for model in models:
                    try:
                        model_id = model.get("id", "")
                        created_at = model.get("createdAt")
                        downloads = model.get("downloads", 0)
                        likes = model.get("likes", 0)

                        # Filtres de qualité
                        if (downloads > 1000 or likes > 10) and created_at:
                            model_date = datetime.fromisoformat(
                                created_at.replace("Z", "+00:00")
                            )

                            if model_date > cutoff_date:
                                # Analyser si c'est un modèle LLM intéressant
                                if self._is_interesting_llm(model_id, model):
                                    _update = ModelUpdate(
                                        model_name=model_id,
                                        provider="huggingface",
                                        version=model.get("sha", "latest")[:8],
                                        release_date=created_at,
                                        capabilities=self._extract_capabilities_hf(
                                            model
                                        ),
                                        performance_improvements=[
                                            "Nouveau modèle tendance sur HF"
                                        ],
                                        breaking_changes=[],
                                        recommended_use_cases=(
                                            self._extract_use_cases_hf(
                                                model_id
                                            )
                                        ),
                                    )
                                    updates.append(update)

                    except Exception as e:
                        logger.debug(
                            "Erreur analyse modèle HF "
                            f"{model.get('id', 'unknown')}: {e}"
                        )
                        continue

                logger.info(
                    f"🤗 Hugging Face: {len(updates)} nouveaux modèles détectés"
                )

        except Exception as e:
            logger.warning(f"⚠️ Erreur vérification HF: {e}")

        return updates

    def _check_openai_updates(self) -> List[ModelUpdate]:
        """Vérifie les nouveaux modèles OpenAI."""
        updates = []

        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                return updates

            headers = {"Authorization": f"Bearer {openai_key}"}
            _response = requests.get(
                self.endpoints["openai"], headers=headers, timeout=10
            )

            if _response.status_code == 200:
                data = _response.json()
                models = data.get("data", [])

                # Récupérer les modèles connus précédemment
                known_models = self._get_known_models("openai")

                new_models = []
                for model in models:
                    model_id = model.get("id", "")

                    # Vérifier si c'est un nouveau modèle intéressant
                    if model_id not in known_models and any(
                        prefix in model_id
                        for prefix in [
                            "gpt-4",
                            "gpt-5",
                            "o1-",
                            "o2-",
                            "chatgpt",
                        ]
                    ):

                        new_models.append(model_id)

                        _update = ModelUpdate(
                            model_name=model_id,
                            provider="openai",
                            version="latest",
                            release_date=datetime.now().isoformat(),
                            capabilities=self._extract_capabilities_openai(
                                model_id
                            ),
                            performance_improvements=["Nouveau modèle OpenAI"],
                            breaking_changes=[],
                            recommended_use_cases=self._extract_use_cases_openai(
                                model_id
                            ),
                        )
                        updates.append(update)

                if new_models:
                    logger.info(
                        f"🤖 OpenAI: {len(new_models)} nouveaux"
                        "modèles: {new_models}"
                    )

        except Exception as e:
            logger.warning(f"⚠️ Erreur vérification OpenAI: {e}")

        return updates

    def _check_gemini_updates(self) -> List[ModelUpdate]:
        """Vérifie les nouveaux modèles Gemini/Google."""
        updates = []

        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                return updates

            url = f"{self.endpoints['google_ai']}?key={gemini_key}"
            _response = requests.get(url, timeout=10)

            if _response.status_code == 200:
                data = _response.json()
                models = data.get("models", [])

                known_models = self._get_known_models("gemini")

                new_models = []
                for model in models:
                    model_name = model.get("name", "").replace("models/", "")

                    if (
                        model_name not in known_models
                        and "gemini" in model_name.lower()
                    ):

                        new_models.append(model_name)

                        _update = ModelUpdate(
                            model_name=model_name,
                            provider="gemini",
                            version=model.get("version", "latest"),
                            release_date=datetime.now().isoformat(),
                            capabilities=self._extract_capabilities_gemini(
                                model
                            ),
                            performance_improvements=["Nouveau modèle Gemini"],
                            breaking_changes=[],
                            recommended_use_cases=self._extract_use_cases_gemini(
                                model_name
                            ),
                        )
                        updates.append(update)

                if new_models:
                    logger.info(
                        f"💎 Gemini: {len(new_models)} nouveaux"
                        "modèles: {new_models}"
                    )

        except Exception as e:
            logger.warning(f"⚠️ Erreur vérification Gemini: {e}")

        return updates

    def _check_anthropic_updates(self) -> List[ModelUpdate]:
        """Vérifie les nouveaux modèles Anthropic Claude."""
        updates = []

        # Modèles Claude 4 récemment sortis (2025)
        latest_claude_models = {
            "claude-opus-4-20250514": {
                "version": "4.0",
                "release_date": "2025-05-14",
                "capabilities": [
                    "superior_reasoning",
                    "multimodal_vision",
                    "extended_thinking",
                    "200k_context",
                    "priority_tier",
                ],
                "performance_improvements": [
                    "Highest level of intelligence and capability",
                    "Advanced reasoning and problem-solving",
                    "Improved multimodal understanding",
                    "Better complex task handling",
                ],
                "breaking_changes": [
                    "Higher cost per token ($15/MTok)",
                    "May require different prompting strategies",
                ],
                "recommended_use_cases": [
                    "Complex reasoning tasks",
                    "Advanced coding projects",
                    "Scientific analysis",
                    "Multimodal content analysis",
                ],
            },
            "claude-sonnet-4-20250514": {
                "version": "4.0",
                "release_date": "2025-05-14",
                "capabilities": [
                    "high_performance",
                    "exceptional_reasoning",
                    "efficiency",
                    "multimodal",
                    "200k_context",
                ],
                "performance_improvements": [
                    "High-performance model with exceptional reasoning",
                    "Better efficiency than Opus",
                    "Faster response times",
                    "Improved cost-performance ratio",
                ],
                "breaking_changes": [
                    "Updated API behavior",
                    "Different output formatting",
                ],
                "recommended_use_cases": [
                    "Balanced performance tasks",
                    "Production applications",
                    "Code review and analysis",
                    "Content generation",
                ],
            },
            "claude-3-7-sonnet-20250219": {
                "version": "3.7",
                "release_date": "2025-02-19",
                "capabilities": [
                    "extended_thinking",
                    "128k_output",
                    "recent_knowledge",
                    "multimodal",
                ],
                "performance_improvements": [
                    "Extended thinking capabilities",
                    "128k token output with beta header",
                    "Latest knowledge cutoff (Nov 2024)",
                    "Enhanced problem-solving",
                ],
                "breaking_changes": [],
                "recommended_use_cases": [
                    "Long-form content generation",
                    "Extended reasoning tasks",
                    "Recent information analysis",
                ],
            },
        }

        # Vérifier les modèles connus
        known_models = self._get_known_models("anthropic")

        for model_name, info in latest_claude_models.items():
            if model_name not in known_models:
                _update = ModelUpdate(
                    model_name=model_name,
                    provider="anthropic",
                    version=info["version"],
                    release_date=info["release_date"],
                    capabilities=info["capabilities"],
                    performance_improvements=info["performance_improvements"],
                    breaking_changes=info["breaking_changes"],
                    recommended_use_cases=info["recommended_use_cases"],
                )
                updates.append(update)

        logger.info(
            f"🏛️ Anthropic: {len(updates)} nouveaux modèles Claude détectés"
        )
        return updates

    def _is_interesting_llm(self, model_id: str, model_data: Dict) -> bool:
        """Détermine si un modèle HF est un LLM intéressant."""

        # Filtres par nom
        interesting_keywords = [
            "llama",
            "mistral",
            "qwen",
            "phi",
            "gemma",
            "claude",
            "gpt",
            "solar",
            "openchat",
            "zephyr",
            "nous",
            "wizard",
            "orca",
            "vicuna",
            "alpaca",
            "falcon",
            "mpt",
            "bloom",
            "t5",
        ]

        model_lower = model_id.lower()
        if not any(keyword in model_lower for keyword in interesting_keywords):
            return False

        # Exclure les modèles trop spécialisés ou de faible qualité
        exclude_keywords = [
            "embedding",
            "classifier",
            "ner",
            "translation",
            "summarization",
            "small",
            "tiny",
            "micro",
            "quantized",
            "ggml",
            "ggu",
        ]

        if any(keyword in model_lower for keyword in exclude_keywords):
            return False

        # Vérifier les métriques de qualité
        downloads = model_data.get("downloads", 0)
        likes = model_data.get("likes", 0)

        return downloads > 100 or likes > 5

    def _extract_capabilities_hf(self, model_data: Dict) -> List[str]:
        """Extrait les capacités d'un modèle HF."""
        capabilities = ["Text generation"]

        # Analyser les tags et la description
        tags = model_data.get("tags", [])
        for tag in tags:
            if "conversational" in tag:
                capabilities.append("Conversation")
            elif "code" in tag:
                capabilities.append("Code generation")
            elif "instruct" in tag:
                capabilities.append("Instruction following")
            elif "multimodal" in tag:
                capabilities.append("Multimodal")

        return capabilities

    def _extract_use_cases_hf(self, model_id: str) -> List[str]:
        """Extrait les cas d'usage d'un modèle HF."""
        model_lower = model_id.lower()
        use_cases = []

        if "code" in model_lower:
            use_cases.extend(["Code generation", "Programming assistance"])
        if "chat" in model_lower or "instruct" in model_lower:
            use_cases.append("Conversational AI")
        if "math" in model_lower:
            use_cases.append("Mathematical reasoning")
        if "creative" in model_lower or "writer" in model_lower:
            use_cases.append("Creative writing")

        if not use_cases:
            use_cases = ["General purpose text generation"]

        return use_cases

    def _extract_capabilities_openai(self, model_id: str) -> List[str]:
        """Extrait les capacités d'un modèle OpenAI."""
        capabilities = ["Text generation", "Conversation"]

        if "gpt-4" in model_id:
            capabilities.extend(
                ["Advanced reasoning", "Code generation", "Multimodal"]
            )
        if "o1" in model_id:
            capabilities.extend(
                ["Complex reasoning", "Mathematical problem solving"]
            )
        if "turbo" in model_id:
            capabilities.append("Fast response")

        return capabilities

    def _extract_use_cases_openai(self, model_id: str) -> List[str]:
        """Extrait les cas d'usage d'un modèle OpenAI."""
        if "o1" in model_id:
            return [
                "Complex reasoning",
                "Mathematical problems",
                "Scientific analysis",
            ]
        elif "gpt-4" in model_id:
            return [
                "General purpose",
                "Code generation",
                "Analysis",
                "Creative tasks",
            ]
        else:
            return ["General conversation", "Simple tasks"]

    def _extract_capabilities_gemini(self, model_data: Dict) -> List[str]:
        """Extrait les capacités d'un modèle Gemini."""
        capabilities = ["Text generation", "Multimodal"]

        model_name = model_data.get("name", "")
        if "pro" in model_name:
            capabilities.extend(["Advanced reasoning", "Long context"])
        if "flash" in model_name:
            capabilities.append("Fast response")
        if "vision" in model_name:
            capabilities.append("Image understanding")

        return capabilities

    def _extract_use_cases_gemini(self, model_name: str) -> List[str]:
        """Extrait les cas d'usage d'un modèle Gemini."""
        use_cases = ["Multimodal tasks", "Text generation"]

        if "pro" in model_name:
            use_cases.extend(["Complex analysis", "Long documents"])
        if "flash" in model_name:
            use_cases.append("Real-time applications")
        if "code" in model_name:
            use_cases.append("Code generation")

        return use_cases

    def _get_known_models(self, provider: str) -> List[str]:
        """Récupère la liste des modèles connus pour un provider."""

        # Récupérer depuis la mémoire
        memory_query = f"modèles connus {provider}"
        memories = self.memory.recall(
            memory_query, memory_types=["knowledge"], limit=10
        )

        known_models = []
        for memory in memories:
            if "modèles" in memory.get("content", ""):
                # Extraire les noms de modèles depuis le contenu
                content = memory["content"]
                # Simple extraction - à améliorer
                for line in content.split("\n"):
                    if provider in line and ":" in line:
                        model_name = line.split(":")[-1].strip()
                        if model_name:
                            known_models.append(model_name)

        # Modèles de base connus
        base_models = {
            "openai": [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-4o",
                "gpt-4o-mini",
            ],
            "anthropic": [
                "claude-3-sonnet",
                "claude-3-opus",
                "claude-3-haiku",
                "claude-3-5-sonnet-20241022",
            ],
            "gemini": [
                "gemini-pro",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-2.0-flash-exp",
            ],
            "huggingface": [],  # Trop nombreux pour lister
        }

        known_models.extend(base_models.get(provider, []))
        return list(set(known_models))  # Déduplication

    def _test_anthropic_model_exists(self, model_name: str) -> bool:
        """Teste si un modèle Anthropic existe via requête test."""
        try:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_key:
                return False

            # Import dynamique d'Anthropic
            try:
                from anthropic import Anthropic

                _client = Anthropic(api_key=anthropic_key)

                # Test avec un prompt très court
                _client.messages.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=1,
                )

                return True  # Si pas d'erreur, le modèle existe

            except Exception as e:
                error_msg = str(e).lower()
                if "model" in error_msg and (
                    "not found" in error_msg or "invalid" in error_msg
                ):
                    return False
                else:
                    # Autre erreur (rate limit, etc.) - on assume que le modèle existe
                    return True

        except Exception:
            return False

    def apply_updates(self, updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Applique les mises à jour de modèles."""

        results = {
            "updated_models": [],
            "failed_updates": [],
            "config_updated": False,
        }

        if not updates:
            return results

        try:
            # Charger la configuration actuelle
            config_path = (
                "/workspaces/appia-dev/src/jarvys_dev/model_config.json"
            )
            with open(config_path) as f:
                current_config = json.load(f)

            original_config = current_config.copy()

            # Appliquer les mises à jour recommandées
            for update in updates:
                try:
                    if (
                        update.provider == "openai"
                        and self._should_update_model(update)
                    ):
                        current_config["openai"] = update.model_name
                        results["updated_models"].append(
                            f"openai: {update.model_name}"
                        )

                    elif (
                        update.provider == "anthropic"
                        and self._should_update_model(update)
                    ):
                        current_config["anthropic"] = update.model_name
                        results["updated_models"].append(
                            f"anthropic: {update.model_name}"
                        )

                    elif (
                        update.provider == "gemini"
                        and self._should_update_model(update)
                    ):
                        current_config["gemini"] = update.model_name
                        results["updated_models"].append(
                            f"gemini: {update.model_name}"
                        )

                except Exception as e:
                    results["failed_updates"].append(
                        f"{update.provider}/{update.model_name}: {e}"
                    )

            # Sauvegarder si des changements ont été effectués
            if current_config != original_config:
                with open(config_path, "w") as f:
                    json.dump(current_config, f, indent=2)

                results["config_updated"] = True

                # Mémoriser la mise à jour
                config_str = json.dumps(current_config)
                self.memory.memorize(
                    "Configuration modèles mise à jour automatiquement: "
                    f"{config_str}",
                    memory_type="experience",
                    importance_score=0.8,
                    tags=["model_update", "config_change", "automation"],
                    metadata={
                        "old_config": original_config,
                        "new_config": current_config,
                    },
                )

                logger.info(
                    f"✅ Configuration mise à jour: {results['updated_models']}"
                )

        except Exception as e:
            logger.error(f"❌ Erreur application mises à jour: {e}")
            results["failed_updates"].append(f"config_update: {e}")

        return results

    def _should_update_model(self, update: ModelUpdate) -> bool:
        """Détermine si une mise à jour doit être appliquée."""

        # Critères pour appliquer automatiquement une mise à jour
        auto_update_criteria = [
            # Nouveaux modèles OpenAI flagrants
            "gpt-5" in update.model_name,
            "o1-pro" in update.model_name or "o2-" in update.model_name,
            # Nouveaux modèles Claude majeurs
            "claude-4" in update.model_name,
            # Nouveaux modèles Gemini majeurs
            "gemini-3" in update.model_name
            or "gemini-2.5" in update.model_name,
        ]

        return any(auto_update_criteria)

    def get_update_report(self) -> str:
        """Génère un rapport des mises à jour disponibles."""

        if not self.available_updates:
            return "Aucune mise à jour de modèle disponible."

        report_lines = [
            "📊 RAPPORT DE MISES À JOUR MODÈLES "
            f"({len(self.available_updates)} disponibles)",
            "=" * 60,
        ]

        # Grouper par provider
        by_provider = {}
        for update in self.available_updates:
            if update.provider not in by_provider:
                by_provider[update.provider] = []
            by_provider[update.provider].append(update)

        for provider, updates in by_provider.items():
            report_lines.append(
                f"\n🔧 {provider.upper()} ({len(updates)} modèles):"
            )

            for update in updates[:3]:  # Top 3 par provider
                report_lines.append(f"  • {update.model_name}")
                report_lines.append(f"    📅 Publié: {update.release_date}")
                report_lines.append(
                    "    🎯 Cas d'usage: "
                    f"{', '.join(update.recommended_use_cases[:2])}"
                )
                report_lines.append(
                    "    ⚡ Améliorations: "
                    f"{', '.join(update.performance_improvements[:1])}"
                )

        report_lines.append(f"\n⏰ Dernière vérification: {self.last_check}")

        return "\n".join(report_lines)


# Instance globale
_auto_updater = None


def get_auto_updater() -> AutoModelUpdater:
    """Récupère l'instance globale de l'auto-updater."""
    global _auto_updater
    if _auto_updater is None:
        _auto_updater = AutoModelUpdater()
    return _auto_updater


if __name__ == "__main__":
    # Test du système de mise à jour
    updater = get_auto_updater()

    print("🔄 Vérification des mises à jour...")
    updates = updater.check_for_updates()

    print(f"\n📊 {len(updates)} mises à jour trouvées")

    if updates:
        print("\n📝 Rapport des mises à jour:")
        print(updater.get_update_report())

        # Test d'application des mises à jour
        print("\n🔧 Application des mises à jour recommandées...")
        results = updater.apply_updates(updates)
        print(f"✅ Résultats: {results}")

    else:
        print("✅ Tous les modèles sont à jour!")
