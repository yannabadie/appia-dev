#!/usr/bin/env python3
"""
Claude 4 Opus Agent - Version directe sans .env
"""

import asyncio
import logging
import os
from datetime import datetime

import anthropic
from github import Github

from supabase import Client, create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeOpusAgent:
    """Agent autonome Claude 4 Opus pour JARVYS"""

    def __init__(self):
        # Utiliser directement les variables d'environnement (pas de .env)
        self.claude = anthropic.AsyncAnthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", "")
        )
        self.github = Github(
            os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
        )

        # Supabase
        try:
            self.supabase: Client = create_client(
                os.environ.get("SUPABASE_URL", ""),
                os.environ.get("SUPABASE_SERVICE_ROLE", ""),
            )
            self.supabase_available = True
            logger.info("✅ Supabase connecté")
        except Exception as e:
            logger.warning(f"⚠️ Supabase non disponible: {e}")
            self.supabase_available = False

        # Configuration avec valeurs par défaut
        self.cost_limit_daily = 3.0  # Valeur fixe
        self.check_interval = 300  # 5 minutes
        self.max_tasks = 3

        # Repos
        self.repos = {"dev": "yannabadie/appia-dev", "ai": "yannabadie/appIA"}

    async def test_claude(self):
        """Test simple de Claude 4 Opus"""
        logger.info("🧪 Test de Claude 4 Opus...")

        try:
            response = await self.claude.messages.create(
                model="claude-opus-4-20250514",  # Claude 4 Opus
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": "Réponds en une ligne: quel modèle es-tu et quelle est ta version?",
                    }
                ],
            )

            logger.info(f"✅ Claude répond: {response.content[0].text}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur Claude: {e}")
            return False

    async def analyze_file(self, file_path: str = "grok_orchestrator.py"):
        """Analyser un fichier avec Claude 4 Opus"""
        logger.info(f"📄 Analyse de {file_path}...")

        try:
            # Lire le fichier
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()[:2000]  # Limiter pour le test
            else:
                logger.error(f"❌ Fichier {file_path} non trouvé")
                return

            # Analyser avec Claude
            response = await self.claude.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyse ce code Python et identifie:
1. Le problème le plus critique
2. Une amélioration simple
3. Une optimisation de performance

Code:
```python
{content}
```

Réponds de manière concise.""",
                    }
                ],
            )

            print("\n" + "=" * 60)
            print("📊 Analyse Claude 4 Opus:")
            print("=" * 60)
            print(response.content[0].text)
            print("=" * 60 + "\n")

            # Sauvegarder l'analyse
            with open(
                f"claude_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md", "w"
            ) as f:
                f.write(f"# Analyse Claude 4 Opus - {file_path}\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(response.content[0].text)

            logger.info("✅ Analyse sauvegardée")

        except Exception as e:
            logger.error(f"❌ Erreur analyse: {e}")

    async def scan_issues(self):
        """Scanner les issues GitHub"""
        logger.info("🔍 Scan des issues GitHub...")

        try:
            repo = self.github.get_repo("yannabadie/appia-dev")
            issues = list(repo.get_issues(state="open"))

            logger.info(f"📋 {len(issues)} issues ouvertes trouvées")

            for issue in issues[:3]:  # Limiter à 3
                print(f"  - #{issue.number}: {issue.title}")

        except Exception as e:
            logger.error(f"❌ Erreur GitHub: {e}")


async def main_menu():
    """Menu principal interactif"""
    print(
        """
    ╔══════════════════════════════════════════════╗
    ║        Claude 4 Opus Agent - JARVYS          ║
    ╠══════════════════════════════════════════════╣
    ║  1. Test de connexion Claude                 ║
    ║  2. Analyser grok_orchestrator.py            ║
    ║  3. Scanner les issues GitHub                ║
    ║  4. Analyser un fichier custom               ║
    ║  5. Tout tester                              ║
    ║  0. Quitter                                  ║
    ╚══════════════════════════════════════════════╝
    """
    )

    # Vérifier les clés
    if not os.environ.get("CLAUDE_API_KEY"):
        print("❌ CLAUDE_API_KEY non trouvée dans l'environnement!")
        print("   Ajoutez-la dans GitHub Codespaces secrets")
        return

    agent = ClaudeOpusAgent()

    while True:
        choice = input("\nVotre choix (0-5): ").strip()

        if choice == "0":
            print("👋 Au revoir!")
            break
        elif choice == "1":
            await agent.test_claude()
        elif choice == "2":
            await agent.analyze_file("grok_orchestrator.py")
        elif choice == "3":
            await agent.scan_issues()
        elif choice == "4":
            file_path = input("Chemin du fichier: ").strip()
            if file_path:
                await agent.analyze_file(file_path)
        elif choice == "5":
            print("\n🚀 Test complet...")
            await agent.test_claude()
            await agent.analyze_file("grok_orchestrator.py")
            await agent.scan_issues()
        else:
            print("❌ Choix invalide")

        input("\n[Appuyez sur Entrée pour continuer]")


if __name__ == "__main__":
    asyncio.run(main_menu())
