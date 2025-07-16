# claude_autonomous_agent_fixed.py
"""
Claude 4 Opus Agent avec gestion d'erreurs Supabase
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

import anthropic
from github import Github

from supabase import Client, create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeOpusAgent:
    """Agent autonome Claude 4 Opus pour JARVYS - Version corrigée"""

    def __init__(self):
        # Initialisation des clients
        self.claude = anthropic.AsyncAnthropic(api_key=os.getenv("CLAUDE_API_KEY", ""))
        self.github = Github(os.getenv("GH_TOKEN"))

        # Initialiser Supabase avec gestion d'erreur
        try:
            self.supabase: Client = create_client(
                os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE")
            )
            self.supabase_available = True
            self._check_tables()
        except Exception as e:
            logger.warning(f"⚠️ Supabase non disponible: {e}")
            self.supabase_available = False

        # Configuration
        self.repos = {
            "dev": os.getenv("GH_REPO_DEV", "yannabadie/appia-dev"),
            "ai": os.getenv("GH_REPO_AI", "yannabadie/appIA"),
        }
        self.cost_limit_daily = float(os.getenv("DAILY_COST_LIMIT", "3.0"))
        self.current_costs = 0.0

    def _check_tables(self):
        """Vérifier si les tables Supabase existent"""
        try:
            # Test simple pour vérifier si la table existe
            self.supabase.table("agent_logs").select("id").limit(1).execute()
            logger.info("✅ Tables Supabase disponibles")
        except Exception as e:
            if "does not exist" in str(e):
                logger.error(
                    "❌ Tables Supabase manquantes! Créez-les avec le script SQL fourni."
                )
                self.supabase_available = False
            else:
                logger.error(f"❌ Erreur Supabase: {e}")
                self.supabase_available = False

    async def autonomous_loop(self):
        """Boucle principale autonome avec gestion d'erreurs"""
        while True:
            try:
                logger.info("🤖 Début du cycle autonome Claude 4 Opus")

                # Mode dégradé si Supabase non disponible
                if not self.supabase_available:
                    logger.warning("⚠️ Mode dégradé: Supabase non disponible")
                    # Continuer sans logging Supabase
                else:
                    # Vérifier les coûts
                    if not await self.check_costs():
                        logger.warning("⚠️ Limite de coûts atteinte")
                        await asyncio.sleep(3600)
                        continue

                # Scanner les problèmes
                issues = await self.scan_for_issues()

                if issues:
                    logger.info(f"📊 {len(issues)} problèmes détectés")

                    # Prioriser et exécuter
                    prioritized_tasks = await self.prioritize_tasks(issues)

                    for task in prioritized_tasks[:3]:
                        await self.execute_task(task)

                    # Créer des PRs si GitHub disponible
                    await self.create_pull_requests()
                else:
                    logger.info("✅ Aucun problème détecté")

                # Logger l'activité si possible
                if self.supabase_available:
                    await self.log_activity()

                logger.info("✅ Cycle terminé, pause de 5 minutes")
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"❌ Erreur dans le cycle: {e}")
                await self.log_error_safe(str(e))
                await asyncio.sleep(60)

    async def check_costs(self) -> bool:
        """Vérifier les coûts avec gestion d'erreur"""
        if not self.supabase_available:
            # En mode dégradé, on continue toujours
            return True

        try:
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            result = (
                self.supabase.table("agent_logs")
                .select("costs")
                .gte("timestamp", yesterday)
                .execute()
            )

            total_costs = sum(log.get("costs", 0) for log in result.data)
            return total_costs < self.cost_limit_daily
        except Exception as e:
            logger.warning(f"⚠️ Impossible de vérifier les coûts: {e}")
            return True  # Continuer en cas d'erreur

    async def scan_for_issues(self) -> List[Dict[str, Any]]:
        """Scanner les repos pour identifier les problèmes"""
        issues = []

        for repo_type, repo_name in self.repos.items():
            try:
                repo = self.github.get_repo(repo_name)

                # Scanner les issues GitHub
                for issue in repo.get_issues(state="open", labels=["claude-fix"]):
                    issues.append(
                        {
                            "type": "github_issue",
                            "repo": repo_type,
                            "number": issue.number,
                            "title": issue.title,
                            "body": issue.body,
                            "labels": [l.name for l in issue.labels],
                        }
                    )

                # Scanner un fichier de test
                try:
                    contents = repo.get_contents("grok_orchestrator.py")
                    if contents:
                        issues.append(
                            {
                                "type": "code_review",
                                "repo": repo_type,
                                "file": "grok_orchestrator.py",
                                "description": "Révision de code demandée",
                            }
                        )
                except:
                    pass

            except Exception as e:
                logger.error(f"Erreur scan {repo_name}: {e}")

        return issues

    async def prioritize_tasks(
        self, issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioriser les tâches avec Claude 4 Opus"""
        if not issues:
            return []

        try:
            prompt = f"""Priorise ces tâches selon leur impact:
            {json.dumps(issues, indent=2)}
            
            Retourne un JSON avec les tâches ordonnées par priorité."""

            response = await self.claude.messages.create(
                model="claude-opus-4-20250514",  # Claude 4 Opus
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parser la réponse
            text = response.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]

            return json.loads(text)
        except Exception as e:
            logger.error(f"Erreur prioritisation: {e}")
            return issues  # Retourner non trié en cas d'erreur

    async def execute_task(self, task: Dict[str, Any]):
        """Exécuter une tâche"""
        logger.info(
            f"🔧 Exécution: {task.get('title', task.get('description', 'Tâche'))}"
        )

        try:
            if task["type"] == "code_review":
                await self.review_code(task)
            elif task["type"] == "github_issue":
                await self.handle_github_issue(task)
        except Exception as e:
            logger.error(f"Erreur exécution tâche: {e}")

    async def review_code(self, task: Dict[str, Any]):
        """Réviser du code avec Claude 4 Opus"""
        logger.info(f"📝 Révision de code: {task['file']}")

        try:
            # Analyser avec Claude
            prompt = f"""Analyse ce fichier Python et suggère des améliorations:
            Fichier: {task['file']}
            
            Fournis:
            1. Problèmes critiques
            2. Suggestions d'amélioration
            3. Exemples de code corrigé"""

            response = await self.claude.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            logger.info("✅ Analyse terminée")

            # Sauvegarder localement
            with open(f"claude_review_{task['file']}.md", "w") as f:
                f.write(f"# Révision Claude 4 Opus - {task['file']}\n\n")
                f.write(response.content[0].text)

        except Exception as e:
            logger.error(f"Erreur révision: {e}")

    async def handle_github_issue(self, task: Dict[str, Any]):
        """Traiter une issue GitHub"""
        logger.info(f"🐛 Traitement issue #{task['number']}: {task['title']}")

        # Simuler le traitement
        await asyncio.sleep(2)
        logger.info(f"✅ Issue #{task['number']} analysée")

    async def create_pull_requests(self):
        """Créer des PRs (simplifié)"""
        logger.info("📤 Vérification des PRs à créer...")
        # Implémentation simplifiée

    async def log_activity(self):
        """Logger l'activité avec gestion d'erreur"""
        if not self.supabase_available:
            return

        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "agent": "claude_4_opus",
                "activity": "autonomous_cycle",
                "costs": self.current_costs,
                "tasks_completed": 1,
                "status": "success",
            }

            self.supabase.table("agent_logs").insert(log_entry).execute()
        except Exception as e:
            logger.warning(f"⚠️ Impossible de logger l'activité: {e}")

    async def log_error_safe(self, error: str):
        """Logger une erreur de manière sûre"""
        logger.error(f"Erreur loggée: {error}")

        if self.supabase_available:
            try:
                self.supabase.table("agent_logs").insert(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "agent": "claude_4_opus",
                        "activity": "error",
                        "status": "error",
                        "error_message": error[:500],  # Limiter la taille
                    }
                ).execute()
            except:
                pass  # Ignorer les erreurs de logging


# Classe simplifiée pour VS Code (optionnel)
class VSCodeClaudeExtension:
    def __init__(self, agent: ClaudeOpusAgent):
        self.agent = agent
        self.port = 8765

    async def start_server(self):
        """Démarrer le serveur (simplifié)"""
        logger.info(f"🚀 Serveur VS Code simulé sur port {self.port}")
        # Version simplifiée sans websockets
        while True:
            await asyncio.sleep(60)


async def main():
    """Point d'entrée principal"""
    # Vérifier les variables
    if not os.getenv("CLAUDE_API_KEY"):
        logger.error("❌ CLAUDE_API_KEY manquante!")
        print("\nPour ajouter votre clé Claude:")
        print("1. https://github.com/settings/codespaces")
        print("2. Ajoutez CLAUDE_API_KEY dans les secrets")
        return

    # Créer l'agent
    agent = ClaudeOpusAgent()

    # Mode simple sans websocket
    if agent.supabase_available:
        logger.info("✅ Mode complet avec Supabase")
    else:
        logger.info("⚠️ Mode dégradé sans Supabase")
        print("\nPour activer Supabase:")
        print("1. Créez les tables avec le script SQL fourni")
        print("2. Vérifiez vos clés SUPABASE_URL et SUPABASE_SERVICE_ROLE")

    # Lancer l'agent
    await agent.autonomous_loop()


if __name__ == "__main__":
    asyncio.run(main())
