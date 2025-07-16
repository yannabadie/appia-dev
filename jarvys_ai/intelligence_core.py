#!/usr/bin/env python3
"""
🧠 JARVYS_AI - Intelligence Core
Module de traitement intelligent et d'analyse des commandes
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import openai

logger = logging.getLogger(__name__)


class IntelligenceCore:
    """
    🧠 Cœur d'intelligence de JARVYS_AI

    Responsable de:
    - Analyse et compréhension des commandes
    - Génération de réponses intelligentes
    - Classification des intentions
    - Apprentissage continu
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialiser le cœur d'intelligence"""
        self.config = config
        self.openai_client = None
        self.is_initialized = False

        # Modèles de classification
        self.command_patterns = {
            "email": [
                "email",
                "mail",
                "message",
                "outlook",
                "gmail",
                "envoyer",
                "recevoir",
            ],
            "file": [
                "fichier",
                "file",
                "dossier",
                "folder",
                "sauvegarder",
                "ouvrir",
                "créer",
            ],
            "cloud": [
                "cloud",
                "gcp",
                "google",
                "deployer",
                "instance",
                "kubernetes",
            ],
            "voice": ["dire", "parler", "voice", "audio", "écouter"],
            "system": ["système", "status", "état", "redémarrer", "arrêter"],
            "general": ["aide", "help", "comment", "quoi", "qui", "pourquoi"],
        }

        logger.info("🧠 Intelligence Core initialisé")

    async def initialize(self):
        """Initialiser les services d'intelligence"""
        try:
            # Configurer OpenAI
            if self.config.get("openai_api_key"):
                openai.api_key = self.config["openai_api_key"]
                self.openai_client = openai
                logger.info("✅ OpenAI configuré")

            self.is_initialized = True
            logger.info("🧠 Intelligence Core prêt")

        except Exception as e:
            logger.error(f"❌ Erreur initialisation Intelligence Core: {e}")
            raise

    async def analyze_command(self, command: str) -> Dict[str, Any]:
        """
        Analyser une commande utilisateur

        Args:
            command: Commande à analyser

        Returns:
            Analyse de la commande avec type, intention, etc.
        """
        try:
            command_lower = command.lower()

            # Classification simple par mots-clés
            command_type = self._classify_command(command_lower)

            # Analyse avancée si OpenAI disponible
            if self.openai_client:
                advanced_analysis = await self._analyze_with_ai(command)
            else:
                advanced_analysis = {"confidence": 0.7, "context": "local"}

            analysis = {
                "type": command_type,
                "original": command,
                "timestamp": datetime.now().isoformat(),
                "confidence": advanced_analysis.get("confidence", 0.7),
                "context": advanced_analysis.get("context", "simple"),
                "entities": self._extract_entities(command),
                "priority": self._determine_priority(command_type),
            }

            logger.info(
                f"📊 Analyse commande: {command_type} (conf: {analysis['confidence']:.2f})"
            )
            return analysis

        except Exception as e:
            logger.error(f"❌ Erreur analyse commande: {e}")
            return {
                "type": "general",
                "original": command,
                "error": str(e),
                "confidence": 0.1,
            }

    def _classify_command(self, command: str) -> str:
        """Classifier la commande par mots-clés"""
        scores = {}

        for cmd_type, keywords in self.command_patterns.items():
            score = sum(1 for keyword in keywords if keyword in command)
            if score > 0:
                scores[cmd_type] = score

        if scores:
            return max(scores, key=scores.get)

        return "general"

    async def _analyze_with_ai(self, command: str) -> Dict[str, Any]:
        """Analyse avancée avec OpenAI"""
        try:
            _response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es JARVYS_AI, assistant de Yann Abadie. Analyse cette commande et détermine son type et contexte.",
                    },
                    {
                        "role": "user",
                        "content": f"Analyse cette commande: {command}",
                    },
                ],
                max_tokens=150,
                temperature=0.3,
            )

            ai_response = response.choices[0].message.content

            return {
                "confidence": 0.9,
                "context": "ai_enhanced",
                "ai_analysis": ai_response,
            }

        except Exception as e:
            logger.warning(f"⚠️ Analyse AI échouée: {e}")
            return {"confidence": 0.7, "context": "fallback"}

    def _extract_entities(self, command: str) -> List[str]:
        """Extraire les entités de la commande"""
        # Extraction simple - peut être améliorée avec NLP
        entities = []

        # Recherche d'emails
        import re

        emails = re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", command
        )
        entities.extend(emails)

        # Recherche de fichiers
        files = re.findall(r"\b\w+\.\w+\b", command)
        entities.extend(files)

        return entities

    def _determine_priority(self, command_type: str) -> str:
        """Déterminer la priorité de la commande"""
        priority_map = {
            "system": "high",
            "email": "medium",
            "cloud": "medium",
            "file": "low",
            "voice": "low",
            "general": "low",
        }

        return priority_map.get(command_type, "low")

    async def process_general_command(self, command: str) -> str:
        """Traiter une commande générale"""
        try:
            if self.openai_client:
                response = await self._generate_ai_response(command)
            else:
                response = self._generate_simple_response(command)

            return response

        except Exception as e:
            logger.error(f"❌ Erreur traitement commande générale: {e}")
            return f"Désolé, je n'ai pas pu traiter votre commande: {e}"

    async def _generate_ai_response(self, command: str) -> str:
        """Générer réponse avec IA"""
        try:
            _response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es JARVYS_AI, l'assistant personnel de Yann Abadie. Tu es professionnel, efficace et bienveillant.",
                    },
                    {"role": "user", "content": command},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Erreur génération IA: {e}")
            return self._generate_simple_response(command)

    def _generate_simple_response(self, command: str) -> str:
        """Générer réponse simple sans IA"""
        responses = {
            "aide": "Je suis JARVYS_AI, votre assistant personnel. Je peux vous aider avec vos emails, fichiers, et tâches quotidiennes.",
            "status": "JARVYS_AI fonctionne normalement. Tous les systèmes sont opérationnels.",
            "bonjour": "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
            "merci": "Je vous en prie ! C'est un plaisir de vous aider.",
        }

        command_lower = command.lower()

        for keyword, response in responses.items():
            if keyword in command_lower:
                return response

<<<<<<< HEAD
        return "Je suis là pour vous aider. Pouvez-vous préciser votre demande ?"
=======
        return (
            "Je suis là pour vous aider. Pouvez-vous préciser votre demande ?"
        )
>>>>>>> origin/main

    def get_stats(self) -> Dict[str, Any]:
        """Obtenir statistiques du cœur d'intelligence"""
        return {
            "is_initialized": self.is_initialized,
            "openai_available": self.openai_client is not None,
            "patterns_loaded": len(self.command_patterns),
            "version": "1.0.0",
        }
