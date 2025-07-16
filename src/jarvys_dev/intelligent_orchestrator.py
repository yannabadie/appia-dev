import sys

"""
Orchestrateur intelligent pour sélection automatique des modèles LLM.
Analyse la tâche et sélectionne le modèle optimal en temps réel.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import requests

logger = logging.getLogger(__name__) = logging.getLogger(__name__)


@dataclass
class ModelCapabilities:
    """Capacités et spécialités d'un modèle."""

    name: str
    provider: str
    reasoning_score: float  # 0-1
    creativity_score: float  # 0-1
    speed_score: float  # 0-1
    multimodal: bool
    max_tokens: int
    cost_per_1k_tokens: float
    specialties: List[str]
    last_updated: str


@dataclass
class TaskAnalysis:
    """Analyse d'une tâche pour sélection de modèle."""

    task_type: str
    complexity: float  # 0-1
    creativity_needed: float  # 0-1
    reasoning_needed: float  # 0-1
    speed_priority: float  # 0-1
    multimodal_needed: bool
    estimated_tokens: int


class IntelligentOrchestrator:
    """Orchestrateur intelligent pour sélection automatique de modèles."""

    def __init__(self):
        self.models_db: Dict[str, ModelCapabilities] = {}
        self.performance_history: List[Dict] = []
        self.last_update = None
        self._initialize_models_database()
        self._load_from_huggingface()

    def _initialize_models_database(self):
        """Initialise la base de données des modèles avec les"
        "dernières capabilities."""

        # Modèles de pointe disponibles (mis à jour avec les dernières versions)
        self.models_db = {
            # OpenAI - Modèles les plus récents
            "gpt-4o": ModelCapabilities(
                name="gpt-4o",
                provider="openai",
                reasoning_score=0.95,
                creativity_score=0.88,
                speed_score=0.85,
                multimodal=True,
                max_tokens=128000,
                cost_per_1k_tokens=0.01,
                specialties=["reasoning", "coding", "analysis", "multimodal"],
                last_updated=datetime.now().isoformat(),
            ),
            "o1-preview": ModelCapabilities(
                name="o1-preview",
                provider="openai",
                reasoning_score=0.98,  # Meilleur raisonnement
                creativity_score=0.82,
                speed_score=0.65,  # Plus lent mais plus précis
                multimodal=False,
                max_tokens=32768,
                cost_per_1k_tokens=0.015,
                specialties=[
                    "complex_reasoning",
                    "mathematics",
                    "scientific_analysis",
                ],
                last_updated=datetime.now().isoformat(),
            ),
            "gpt-4o-mini": ModelCapabilities(
                name="gpt-4o-mini",
                provider="openai",
                reasoning_score=0.88,
                creativity_score=0.85,
                speed_score=0.95,  # Très rapide
                multimodal=True,
                max_tokens=128000,
                cost_per_1k_tokens=0.0001,  # Très économique
                specialties=["fast_tasks", "simple_coding", "chat"],
                last_updated=datetime.now().isoformat(),
            ),
            # Anthropic Claude 4 - Nouvelles versions 2025
            "claude-opus-4-20250514": ModelCapabilities(
                name="claude-opus-4-20250514",
                provider="anthropic",
                reasoning_score=0.98,  # Nouveau modèle le plus puissant
                creativity_score=0.95,
                speed_score=0.75,
                multimodal=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.015,  # $15/MTok input
                specialties=[
                    "superior_reasoning",
                    "complex_problem_solving",
                    "advanced_coding",
                    "multimodal_analysis",
                ],
                last_updated="2025-05-14",
            ),
            "claude-sonnet-4-20250514": ModelCapabilities(
                name="claude-sonnet-4-20250514",
                provider="anthropic",
                reasoning_score=0.96,
                creativity_score=0.93,
                speed_score=0.88,
                multimodal=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.003,  # $3/MTok input
                specialties=[
                    "high_performance",
                    "exceptional_reasoning",
                    "efficiency",
                    "balanced_tasks",
                ],
                last_updated="2025-05-14",
            ),
            "claude-3-7-sonnet-20250219": ModelCapabilities(
                name="claude-3-7-sonnet-20250219",
                provider="anthropic",
                reasoning_score=0.94,
                creativity_score=0.91,
                speed_score=0.90,
                multimodal=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.003,
                specialties=[
                    "extended_thinking",
                    "high_performance",
                    "128k_output",
                    "recent_knowledge",
                ],
                last_updated="2025-02-19",
            ),
            "claude-3-5-sonnet-20241022": ModelCapabilities(
                name="claude-3-5-sonnet-20241022",
                provider="anthropic",
                reasoning_score=0.93,
                creativity_score=0.92,
                speed_score=0.82,
                multimodal=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.003,
                specialties=[
                    "creative_writing",
                    "code_review",
                    "long_context",
                    "ethics",
                ],
                last_updated="2024-10-22",
            ),
            # Google Gemini 2.5 - Dernières versions avec thinking
            "gemini-2.5-pro": ModelCapabilities(
                name="gemini-2.5-pro",
                provider="gemini",
                reasoning_score=0.97,  # Nouveau modèle le plus puissant de Google
                creativity_score=0.91,
                speed_score=0.82,
                multimodal=True,
                max_tokens=2000000,  # Énorme contexte
                cost_per_1k_tokens=0.002,
                specialties=[
                    "enhanced_thinking",
                    "maximum_accuracy",
                    "complex_coding",
                    "multimodal_understanding",
                    "large_databases",
                ],
                last_updated="2025-01-01",
            ),
            "gemini-2.5-flash": ModelCapabilities(
                name="gemini-2.5-flash",
                provider="gemini",
                reasoning_score=0.94,
                creativity_score=0.89,
                speed_score=0.95,
                multimodal=True,
                max_tokens=1000000,
                cost_per_1k_tokens=0.0005,
                specialties=[
                    "adaptive_thinking",
                    "cost_efficiency",
                    "high_volume_tasks",
                    "price_performance",
                ],
                last_updated="2025-01-01",
            ),
            "gemini-2.0-flash-exp": ModelCapabilities(
                name="gemini-2.0-flash-exp",
                provider="gemini",
                reasoning_score=0.90,
                creativity_score=0.89,
                speed_score=0.92,
                multimodal=True,
                max_tokens=1000000,
                cost_per_1k_tokens=0.0005,
                specialties=[
                    "multimodal",
                    "large_context",
                    "realtime",
                    "video_analysis",
                ],
                last_updated="2024-12-01",
            ),
            # Grok
            "grok-4": ModelCapabilities(
                name="grok-4",
                provider="grok",
                reasoning_score=0.92,
                creativity_score=0.90,
                speed_score=0.88,
                multimodal=False,
                max_tokens=8192,
                cost_per_1k_tokens=0.0,  # Assuming free for now
                specialties=["realtime", "humor", "unfiltered"],
                last_updated=datetime.now().isoformat(),
            ),
        }

        logger = logging.getLogger(__name__).info(f"🧠 Orchestrateur initialisé avec {len(self.models_db)} modèles")

    def _load_from_huggingface(self):
        """Met à jour la base de modèles depuis Hugging Face."""
        try:
            # Récupérer les modèles tendance depuis HF
            hf_url = "https://huggingface.co/api/models"
            params = {
                "sort": "trending",
                "filter": "text-generation",
                "limit": 20,
            }

            _response = requests.get(hf_url, params=params, timeout=10)
            if _response.status_code == 200:
                trending_models = _response.json()
                logger = logging.getLogger(__name__).info(f"📈 Récupéré {len(trending_models)} modèles tendance HF")

                # Analyser les nouveaux modèles pour mise à jour future
                self._analyze_hf_models(trending_models)

        except Exception as e:
            logger = logging.getLogger(__name__).warning(f"⚠️ Erreur récupération HF: {e}")

    def _analyze_hf_models(self, models: List[Dict]):
        """Analyse les modèles HF pour détecter les nouveaux."""
        new_models = []
        for model in models:
            model_id = model.get("id", "")
            if any(
                keyword in model_id.lower()
                for keyword in ["gpt", "claude", "gemini", "llama", "mistral"]
            ):
                new_models.append(
                    {
                        "id": model_id,
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "created_at": model.get("createdAt"),
                    }
                )

        if new_models:
            logger = logging.getLogger(__name__).info(f"🆕 Détecté {len(new_models)} nouveaux modèles potentiels")

    def analyze_task(self, prompt: str, task_type: str = "auto") -> TaskAnalysis:
        """Analyse une tâche pour déterminer les besoins."""

        # Détection automatique du type de tâche
        if task_type == "auto":
            task_type = self._detect_task_type(prompt)

        # Analyse de complexité
        complexity = self._estimate_complexity(prompt)

        # Besoins en créativité
        creativity_needed = self._estimate_creativity_need(prompt, task_type)

        # Besoins en raisonnement
        reasoning_needed = self._estimate_reasoning_need(prompt, task_type)

        # Priorité vitesse
        speed_priority = self._estimate_speed_priority(prompt, task_type)

        # Multimodal nécessaire
        multimodal_needed = self._detect_multimodal_need(prompt)

        # Estimation de tokens
        estimated_tokens = len(prompt.split()) * 1.3  # Approximation

        return TaskAnalysis(
            task_type=task_type,
            complexity=complexity,
            creativity_needed=creativity_needed,
            reasoning_needed=reasoning_needed,
            speed_priority=speed_priority,
            multimodal_needed=multimodal_needed,
            estimated_tokens=int(estimated_tokens),
        )

    def _detect_task_type(self, prompt: str) -> str:
        """Détecte automatiquement le type de tâche."""
        prompt_lower = prompt.lower()

        # Patterns de détection
        if any(
            kw in prompt_lower
            for kw in ["code", "function", "debug", "programming", "script"]
        ):
            return "coding"
        elif any(
            kw in prompt_lower
            for kw in ["math", "calculate", "solve", "equation", "algorithm"]
        ):
            return "mathematical"
        elif any(
            kw in prompt_lower
            for kw in [
                "create",
                "write",
                "story",
                "poem",
                "creative",
                "imagine",
            ]
        ):
            return "creative"
        elif any(
            kw in prompt_lower
            for kw in ["analyze", "reason", "explain", "why", "how", "complex"]
        ):
            return "reasoning"
        elif any(
            kw in prompt_lower
            for kw in ["image", "video", "visual", "picture", "diagram"]
        ):
            return "multimodal"
        elif any(
            kw in prompt_lower for kw in ["quick", "fast", "simple", "brie", "summary"]
        ):
            return "fast"
        else:
            return "general"

    def _estimate_complexity(self, prompt: str) -> float:
        """Estime la complexité de la tâche (0-1)."""
        factors = []

        # Longueur du prompt
        length_factor = min(len(prompt) / 2000, 1.0)
        factors.append(length_factor)

        # Mots complexes
        complex_words = [
            "algorithm",
            "architecture",
            "optimization",
            "analysis",
            "synthesis",
        ]
        complex_count = sum(1 for word in complex_words if word in prompt.lower())
        complexity_factor = min(complex_count / len(complex_words), 1.0)
        factors.append(complexity_factor)

        # Questions multiples
        question_count = prompt.count("?")
        question_factor = min(question_count / 5, 1.0)
        factors.append(question_factor)

        return sum(factors) / len(factors)

    def _estimate_creativity_need(self, prompt: str, task_type: str) -> float:
        """Estime le besoin en créativité (0-1)."""
        if task_type in ["creative", "writing"]:
            return 0.9
        elif task_type in ["coding", "mathematical"]:
            return 0.3
        elif any(
            kw in prompt.lower()
            for kw in ["creative", "innovative", "original", "unique"]
        ):
            return 0.8
        else:
            return 0.5

    def _estimate_reasoning_need(self, prompt: str, task_type: str) -> float:
        """Estime le besoin en raisonnement (0-1)."""
        if task_type in ["mathematical", "reasoning", "coding"]:
            return 0.9
        elif any(
            kw in prompt.lower() for kw in ["why", "how", "explain", "analyze", "logic"]
        ):
            return 0.8
        else:
            return 0.6

    def _estimate_speed_priority(self, prompt: str, task_type: str) -> float:
        """Estime la priorité vitesse (0-1)."""
        if task_type == "fast":
            return 0.9
        elif any(
            kw in prompt.lower()
            for kw in ["quick", "fast", "urgent", "now", "immediately"]
        ):
            return 0.8
        elif any(
            kw in prompt.lower()
            for kw in ["detailed", "thorough", "comprehensive", "deep"]
        ):
            return 0.2
        else:
            return 0.5

    def _detect_multimodal_need(self, prompt: str) -> bool:
        """Détecte si la tâche nécessite du multimodal."""
        multimodal_keywords = [
            "image",
            "picture",
            "photo",
            "video",
            "visual",
            "diagram",
            "chart",
            "graph",
        ]
        return any(kw in prompt.lower() for kw in multimodal_keywords)

    def select_optimal_model(
        self, task_analysis: TaskAnalysis
    ) -> Tuple[str, ModelCapabilities, float]:
        """Sélectionne le modèle optimal pour une tâche."""

        best_model = None
        best_score = 0
        best_name = ""

        for model_name, model in self.models_db.items():
            score = self._calculate_model_score(model, task_analysis)

            if score > best_score:
                best_score = score
                best_model = model
                best_name = model_name

        logger = logging.getLogger(__name__).info(
            f"🎯 Modèle optimal sélectionné: {best_name} (score:" "{best_score:.2f})"
        )
        return best_name, best_model, best_score

    def _calculate_model_score(
        self, model: ModelCapabilities, task: TaskAnalysis
    ) -> float:
        """Calcule le score d'adéquation modèle-tâche."""

        scores = []

        # Score raisonnement
        reasoning_score = model.reasoning_score * task.reasoning_needed
        scores.append(reasoning_score)

        # Score créativité
        creativity_score = model.creativity_score * task.creativity_needed
        scores.append(creativity_score)

        # Score vitesse
        speed_score = model.speed_score * task.speed_priority
        scores.append(speed_score)

        # Bonus multimodal si nécessaire
        if task.multimodal_needed:
            multimodal_bonus = 0.8 if model.multimodal else 0.0
            scores.append(multimodal_bonus)

        # Pénalité coût pour tâches simples
        if task.complexity < 0.3:
            cost_penalty = max(0, 1 - model.cost_per_1k_tokens * 100)
            scores.append(cost_penalty)

        # Score spécialité
        specialty_bonus = 0
        if task.task_type in model.specialties:
            specialty_bonus = 0.2
        scores.append(specialty_bonus)

        # Score final
        final_score = sum(scores) / len(scores)

        # Ajustement historique de performance
        historical_bonus = self._get_historical_performance(model.name)
        final_score += historical_bonus

        return min(final_score, 1.0)

    def _get_historical_performance(self, model_name: str) -> float:
        """Récupère le bonus de performance historique."""
        # Simulé pour l'instant - à implémenter avec données réelles
        recent_performances = [
            p for p in self.performance_history if p.get("model") == model_name
        ]

        if recent_performances:
            avg_success = sum(
                p.get("success", 0.5) for p in recent_performances[-10:]
            ) / min(len(recent_performances), 10)
            return (avg_success - 0.5) * 0.1  # Bonus/malus de 10%

        return 0.0

    def record_performance(
        self,
        model_name: str,
        task_type: str,
        success_rate: float,
        latency: float,
        cost: float,
    ):
        """Enregistre la performance d'un modèle pour apprentissage."""

        performance = {
            "model": model_name,
            "task_type": task_type,
            "success": success_rate,
            "latency": latency,
            "cost": cost,
            "timestamp": datetime.now().isoformat(),
        }

        self.performance_history.append(performance)

        # Garder seulement les 1000 dernières performances
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]

        logger = logging.getLogger(__name__).info(
            f"📊 Performance enregistrée: {model_name} - {task_type} - "
            f"{success_rate:.2f}"
        )

    def update_models_database(self):
        """Met à jour la base de données des modèles."""
        try:
            # Vérifier les nouveaux modèles OpenAI
            self._check_openai_updates()

            # Vérifier les nouveaux modèles Anthropic
            self._check_anthropic_updates()

            # Vérifier les nouveaux modèles Gemini
            self._check_gemini_updates()

            # Mise à jour depuis Hugging Face
            self._load_from_huggingface()

            self.last_update = datetime.now().isoformat()
            logger = logging.getLogger(__name__).info(f"🔄 Base de modèles mise à jour: {self.last_update}")

        except Exception as e:
            logger = logging.getLogger(__name__).error(f"❌ Erreur mise à jour modèles: {e}")

    def _check_openai_updates(self):
        """Vérifie les nouveaux modèles OpenAI."""
        try:
            # Cette API nécessite une clé OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                return

            headers = {"Authorization": f"Bearer {openai_key}"}
            _response = requests.get(
                "https://api.openai.com/v1/models", headers=headers, timeout=10
            )

            if _response.status_code == 200:
                models = _response.json().get("data", [])
                logger = logging.getLogger(__name__).info(f"🤖 Récupéré {len(models)} modèles OpenAI")

                # Analyser pour nouveaux modèles GPT-4, o1, etc.
                for model in models:
                    model_id = model.get("id", "")
                    if any(prefix in model_id for prefix in ["gpt-4", "o1-", "gpt-5"]):
                        if model_id not in self.models_db:
                            logger = logging.getLogger(__name__).info(f"🆕 Nouveau modèle OpenAI détecté: {model_id}")

        except Exception as e:
            logger = logging.getLogger(__name__).warning(f"⚠️ Erreur vérification OpenAI: {e}")

    def _check_anthropic_updates(self):
        """Vérifie les nouveaux modèles Anthropic."""
        # Anthropic ne fournit pas d'API publique pour lister les modèles
        # On peut surveiller leur blog/docs pour les nouveautés
        logger = logging.getLogger(__name__).info("🔍 Vérification manuelle recommandée pour nouveaux modèles Claude")

    def _check_gemini_updates(self):
        """Vérifie les nouveaux modèles Gemini."""
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                return

            # API Google AI Studio pour lister les modèles
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models"
                f"?key={gemini_key}"
            )
            _response = requests.get(url, timeout=10)

            if _response.status_code == 200:
                data = _response.json()
                models = data.get("models", [])
                logger = logging.getLogger(__name__).info(f"💎 Récupéré {len(models)} modèles Gemini")

                for model in models:
                    model_name = model.get("name", "").replace("models/", "")
                    if "gemini" in model_name and model_name not in self.models_db:
                        logger = logging.getLogger(__name__).info(f"🆕 Nouveau modèle Gemini détecté: {model_name}")

        except Exception as e:
            logger = logging.getLogger(__name__).warning(f"⚠️ Erreur vérification Gemini: {e}")

    def get_orchestrator_stats(self) -> Dict:
        """Retourne les statistiques de l'orchestrateur."""
        return {
            "total_models": len(self.models_db),
            "performance_history_count": len(self.performance_history),
            "last_update": self.last_update,
            "models_by_provider": {
                provider: len(
                    [m for m in self.models_db.values() if m.provider == provider]
                )
                for provider in set(m.provider for m in self.models_db.values())
            },
            "avg_scores": {
                "reasoning": (
                    sum(m.reasoning_score for m in self.models_db.values())
                    / len(self.models_db)
                ),
                "creativity": (
                    sum(m.creativity_score for m in self.models_db.values())
                    / len(self.models_db)
                ),
                "speed": (
                    sum(m.speed_score for m in self.models_db.values())
                    / len(self.models_db)
                ),
            },
        }


# Instance globale de l'orchestrateur
_orchestrator_instance = None


def get_orchestrator() -> IntelligentOrchestrator:
    """Retourne l'instance globale de l'orchestrateur."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = IntelligentOrchestrator()
    return _orchestrator_instance


def reset_orchestrator():
    """Remet à zéro l'instance globale."""
    global _orchestrator_instance
    _orchestrator_instance = None


__all__ = [
    "IntelligentOrchestrator",
    "TaskAnalysis",
    "ModelCapabilities",
    "get_orchestrator",
    "reset_orchestrator",
]


if __name__ == "__main__":
    # Test de l'orchestrateur
    orchestrator = get_orchestrator()

    # Test d'analyse de tâche
    test_prompts = [
        ("Écris une fonction Python pour trier une liste", "coding"),
        (
            "Résous cette équation complexe: x^3 + 2x^2 - 5x + 1 = 0",
            "mathematical",
        ),
        ("Écris un poème sur l'intelligence artificielle", "creative"),
        ("Analyse cette image et décris ce que tu vois", "multimodal"),
        ("Donne-moi un résumé rapide", "fast"),
    ]

    for prompt, expected_type in test_prompts:
        task_analysis = orchestrator.analyze_task(prompt)
        model_name, model, score = orchestrator.select_optimal_model(task_analysis)

        print(f"\n📝 Prompt: {prompt[:50]}...")
        print(f"🎯 Type détecté: {task_analysis.task_type}")
        print(f"🤖 Modèle sélectionné: {model_name}")
        print(f"📊 Score: {score:.2f}")
        print(f"🔧 Spécialités: {model.specialties}")

    # Stats
    stats = orchestrator.get_orchestrator_stats()
    print("\n📊 Stats orchestrateur:")
    print(json.dumps(stats, indent=2))
