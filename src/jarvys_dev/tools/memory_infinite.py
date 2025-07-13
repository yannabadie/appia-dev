"""
Outils de gestion de la mémoire infinie partagée entre JARVYS_DEV et JARVYS_AI.
Utilise Supabase comme base vectorielle pour persistance et recherche sémantique.
"""

import hashlib
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import openai

from supabase import Client, create_client

logger = logging.getLogger(__name__)


class JarvysInfiniteMemory:
    """Gestionnaire de mémoire infinie partagée pour l'écosystème JARVYS."""

    def __init__(
        self, agent_name: str = "JARVYS_DEV", user_context: str = "default"
    ):
        self.agent_name = agent_name
        self.user_context = user_context
        self.supabase: Optional[Client] = None
        self.openai_client = None

        # Initialisation Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                logger.info(
                    f"✅ Mémoire infinie initialisée pour {agent_name}"
                )
            except Exception as e:
                logger.error(f"❌ Erreur connexion Supabase: {e}")

        # Initialisation OpenAI pour embeddings
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)

    def memorize(
        self,
        content: str,
        memory_type: str = "experience",
        importance_score: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Mémorise une information dans la mémoire infinie.

        Args:
            content: Le contenu à mémoriser
            memory_type: Type de mémoire ('conversation', 'preference', 'knowledge', 'experience')
            importance_score: Score d'importance (0.0 à 1.0)
            tags: Tags pour catégoriser
            metadata: Métadonnées additionnelles

        Returns:
            True si succès, False sinon
        """
        if not self.supabase or not self.openai_client:
            logger.warning(
                "Mémoire non disponible (Supabase ou OpenAI manquant)"
            )
            return False

        try:
            # Générer l'embedding
            embedding = self._generate_embedding(content)
            if not embedding:
                return False

            # Préparer les données
            memory_data = {
                "content": content,
                "agent_source": self.agent_name,
                "memory_type": memory_type,
                "user_context": self.user_context,
                "importance_score": importance_score,
                "tags": tags or [],
                "metadata": metadata or {},
                "embedding": embedding,
            }

            # Insérer dans Supabase
            _result = (
                self.supabase.table("jarvys_memory")
                .insert(memory_data)
                .execute()
            )

            if result.data:
                logger.info(f"💾 Mémoire sauvegardée: {content[:50]}...")
                return True
            else:
                logger.error(f"❌ Échec sauvegarde mémoire: {result}")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur mémorisation: {e}")
            return False

    def recall(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        min_importance: float = 0.0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Recherche dans la mémoire infinie.

        Args:
            query: Requête de recherche
            memory_types: Types de mémoire à rechercher
            min_importance: Score d'importance minimum
            limit: Nombre maximum de résultats

        Returns:
            Liste des souvenirs trouvés
        """
        if not self.supabase or not self.openai_client:
            logger.warning("Mémoire non disponible pour la recherche")
            return []

        try:
            # Générer l'embedding de la requête
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return []

            # Construire la requête Supabase
            query_builder = (
                self.supabase.table("jarvys_memory")
                .select("*")
                .eq("user_context", self.user_context)
                .gte("importance_score", min_importance)
                .order("created_at", desc=True)
                .limit(limit)
            )

            # Filtrer par type de mémoire si spécifié
            if memory_types:
                query_builder = query_builder.in_("memory_type", memory_types)

            _result = query_builder.execute()

            if result.data:
                # Calculer la similarité et trier
                memories = []
                for memory in result.data:
                    if memory.get("embedding"):
                        similarity = self._calculate_similarity(
                            query_embedding, memory["embedding"]
                        )
                        memory["similarity"] = similarity
                        memories.append(memory)

                # Trier par similarité décroissante
                memories.sort(key=lambda x: x["similarity"], reverse=True)

                logger.info(
                    f"🧠 {len(memories)} souvenirs trouvés pour:"
                    "{query[:30]}..."
                )
                return memories[:limit]

            return []

        except Exception as e:
            logger.error(f"❌ Erreur recherche mémoire: {e}")
            return []

    def get_memory_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la mémoire."""
        if not self.supabase:
            return {"error": "Mémoire non disponible"}

        try:
            # Nombre total de souvenirs
            total_result = (
                self.supabase.table("jarvys_memory")
                .select("id", count="exact")
                .eq("user_context", self.user_context)
                .execute()
            )

            # Souvenirs par agent
            agents_result = (
                self.supabase.table("jarvys_memory")
                .select("agent_source", count="exact")
                .eq("user_context", self.user_context)
                .execute()
            )

            # Souvenirs par type
            types_result = (
                self.supabase.table("jarvys_memory")
                .select("memory_type", count="exact")
                .eq("user_context", self.user_context)
                .execute()
            )

            return {
                "total_memories": total_result.count or 0,
                "by_agent": {
                    item["agent_source"]: item["count"]
                    for item in agents_result.data or []
                },
                "by_type": {
                    item["memory_type"]: item["count"]
                    for item in types_result.data or []
                },
                "user_context": self.user_context,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Erreur stats mémoire: {e}")
            return {"error": str(e)}

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Génère un embedding pour le texte."""
        if not self.openai_client:
            return None

        try:
            _response = self.openai_client.embeddings.create(
                model="text-embedding-3-small", input=text
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"❌ Erreur génération embedding: {e}")
            return None

    def _calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """Calcule la similarité cosinus entre deux embeddings."""
        try:
            import numpy as np

            # Normaliser les vecteurs
            a = np.array(embedding1)
            b = np.array(embedding2)

            # Similarité cosinus
            similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            return float(similarity)

        except Exception:
            return 0.0

    def log_interaction(
        self, interaction_type: str, content: str, success: bool = True
    ):
        """Log une interaction pour le monitoring."""
        if not self.supabase:
            return

        try:
            self.supabase.table("jarvys_metrics").insert(
                {
                    "agent_type": self.agent_name,
                    "event_type": "memory_operation",
                    "service": "supabase",
                    "success": success,
                    "metadata": {
                        "interaction_type": interaction_type,
                        "content_hash": hashlib.md5(
                            content.encode()
                        ).hexdigest()[:8],
                    },
                    "user_context": self.user_context,
                }
            ).execute()

        except Exception as e:
            logger.error(f"❌ Erreur log interaction: {e}")


# Instance globale pour JARVYS_DEV
_memory_instance = None


def get_memory(
    agent_name: str = "JARVYS_DEV", user_context: str = "default"
) -> JarvysInfiniteMemory:
    """Récupère l'instance de mémoire (singleton par agent/user)."""
    global _memory_instance

    if _memory_instance is None or _memory_instance.agent_name != agent_name:
        _memory_instance = JarvysInfiniteMemory(agent_name, user_context)

    return _memory_instance


# Fonctions de compatibilité avec l'ancien code
def memory_search(
    query: str, user_context: str = "default"
) -> List[Dict[str, Any]]:
    """Recherche dans la mémoire (fonction de compatibilité)."""
    memory = get_memory("JARVYS_DEV", user_context)
    return memory.recall(query)


def upsert_embedding(content: str, user_context: str = "default") -> bool:
    """Mémorise du contenu (fonction de compatibilité)."""
    memory = get_memory("JARVYS_DEV", user_context)
    return memory.memorize(content, memory_type="knowledge")


def get_memory_context(user_context: str = "default") -> str:
    """Récupère le contexte de mémoire récent pour un utilisateur."""
    memory = get_memory("JARVYS_DEV", user_context)
    recent_memories = memory.recall(
        "contexte récent conversation",
        memory_types=["conversation", "preference"],
        limit=5,
    )

    if recent_memories:
        context_parts = []
        for mem in recent_memories:
            context_parts.append(f"{mem['memory_type']}: {mem['content']}")
        return "\n".join(context_parts)

    return "Aucun contexte de mémoire disponible."


if __name__ == "__main__":
    # Test de la mémoire infinie
    memory = get_memory("JARVYS_DEV", "test_user")

    # Test mémorisation
    success = memory.memorize(
        "L'utilisateur préfère les solutions simples et épurées",
        memory_type="preference",
        importance_score=0.8,
        tags=["preferences", "ui", "design"],
    )
    print(f"Mémorisation: {'✅' if success else '❌'}")

    # Test recherche
    results = memory.recall("préférences utilisateur", limit=3)
    print(f"Recherche: {len(results)} résultats trouvés")

    # Stats
    stats = memory.get_memory_stats()
    print(f"Stats: {stats}")
