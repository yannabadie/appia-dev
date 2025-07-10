#!/usr/bin/env python3
"""
Script de démarrage complet pour l'écosystème JARVYS_DEV.
Lance l'agent autonome, le serveur MCP, et le dashboard de monitoring.
"""

import argparse
import asyncio
import logging
import multiprocessing
import os
import signal
import sys
import time
from pathlib import Path

import uvicorn

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("jarvys_ecosystem.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("JARVYS_ECOSYSTEM")

# Ajout du chemin src
sys.path.insert(0, str(Path(__file__).parent / "src"))


def check_environment():
    """Vérifie que toutes les variables d'environnement requises sont définies."""
    required_vars = [
        "GITHUB_TOKEN",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "GCP_SA_JSON",
        "GEMINI_API_KEY",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Variables d'environnement manquantes: {missing_vars}")
        logger.error("Consultez le README.md pour la configuration complète")
        return False

    logger.info("✅ Toutes les variables d'environnement sont définies")
    return True


def run_langgraph_agent():
    """Lance l'agent LangGraph autonome."""
    try:
        logger.info("🤖 Démarrage de l'agent LangGraph...")
        from jarvys_dev.langgraph_loop import run_loop

        asyncio.run(run_loop())
    except Exception as e:
        logger.error(f"❌ Erreur dans l'agent LangGraph: {e}")


def run_mcp_server():
    """Lance le serveur MCP (Model Context Protocol)."""
    try:
        logger.info("🔗 Démarrage du serveur MCP...")
        from app.main import app

        uvicorn.run(app, host="0.0.0.0", port=54321, log_level="info")
    except Exception as e:
        logger.error(f"❌ Erreur dans le serveur MCP: {e}")


def run_dashboard():
    """Lance le dashboard de monitoring."""
    try:
        logger.info("📊 Démarrage du dashboard...")
        from dashboard.main import app, metrics

        # Initialiser quelques métriques d'exemple
        metrics.log_api_call(
            service="github",
            model="api",
            endpoint="/repos",
            tokens=0,
            cost=0.0,
            response_time=250,
        )

        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
    except Exception as e:
        logger.error(f"❌ Erreur dans le dashboard: {e}")


def run_model_watcher():
    """Lance le surveillant de modèles."""
    try:
        logger.info("👁️ Démarrage du surveillant de modèles...")
        from jarvys_dev.model_watcher import main

        main()
    except Exception as e:
        logger.error(f"❌ Erreur dans le surveillant de modèles: {e}")


def signal_handler(signum, frame):
    """Gestionnaire pour arrêt propre."""
    logger.info("🛑 Arrêt de l'écosystème JARVYS_DEV...")
    sys.exit(0)


def main():
    """Fonction principale de démarrage."""
    parser = argparse.ArgumentParser(
        description="Lance l'écosystème complet JARVYS_DEV"
    )
    parser.add_argument(
        "--component",
        choices=["all", "agent", "mcp", "dashboard", "watcher"],
        default="all",
        help="Composant à lancer (défaut: all)",
    )
    parser.add_argument(
        "--skip-env-check",
        action="store_true",
        help="Ignorer la vérification des variables d'environnement",
    )

    args = parser.parse_args()

    # Configuration du gestionnaire de signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🚀 Démarrage de l'écosystème JARVYS_DEV")
    logger.info("=" * 60)

    # Vérification de l'environnement
    if not args.skip_env_check and not check_environment():
        sys.exit(1)

    if args.component == "all":
        logger.info("🔄 Lancement de tous les composants...")

        # Créer les processus pour chaque composant
        processes = []

        # Agent LangGraph
        agent_process = multiprocessing.Process(
            target=run_langgraph_agent, name="LangGraph-Agent"
        )
        processes.append(agent_process)

        # Serveur MCP
        mcp_process = multiprocessing.Process(
            target=run_mcp_server, name="MCP-Server"
        )
        processes.append(mcp_process)

        # Dashboard
        dashboard_process = multiprocessing.Process(
            target=run_dashboard, name="Dashboard"
        )
        processes.append(dashboard_process)

        # Surveillant de modèles
        watcher_process = multiprocessing.Process(
            target=run_model_watcher, name="Model-Watcher"
        )
        processes.append(watcher_process)

        # Démarrer tous les processus
        for process in processes:
            process.start()
            logger.info(f"✅ {process.name} démarré (PID: {process.pid})")

        logger.info("🌟 Écosystème JARVYS_DEV complètement opérationnel !")
        logger.info("📊 Dashboard: http://localhost:8080")
        logger.info("🔗 Serveur MCP: http://localhost:54321")
        logger.info("🤖 Agent autonome en fonctionnement")
        logger.info("👁️ Surveillant de modèles actif")

        try:
            # Attendre que tous les processus se terminent
            for process in processes:
                process.join()
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt demandé, fermeture des processus...")
            for process in processes:
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    logger.warning(f"⚠️ Arrêt forcé de {process.name}")
                    process.kill()

    elif args.component == "agent":
        run_langgraph_agent()
    elif args.component == "mcp":
        run_mcp_server()
    elif args.component == "dashboard":
        run_dashboard()
    elif args.component == "watcher":
        run_model_watcher()

    logger.info("👋 Écosystème JARVYS_DEV arrêté")


if __name__ == "__main__":
    main()
