#!/usr/bin/env python3
"""
🤖 JARVYS Orchestrator Autonome GCP
==================================

Version autonome de l'orchestrateur JARVYS pour Google Cloud Platform.
Fonctionne 24/7 indépendamment de GitHub Codespace ou machine locale.

Architecture:
- Hébergé sur Cloud Run GCP
- Communication via Supabase
- Interface WebSocket temps réel
- Monitoring et alertes inclus

Usage:
    python grok_orchestrator_gcp.py

Features:
- ✅ Autonomie complète 24/7
- ✅ Communication temps réel
- ✅ Interface dashboard intégrée
- ✅ Monitoring et logs centralisés
- ✅ Auto-restart et high availability
"""

import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from github_sync_manager import GitHubSyncManager, setup_github_sync
from pydantic import BaseModel

from supabase import Client, create_client

# Configuration GCP
PORT = int(os.getenv("PORT", 8080))  # Cloud Run utilise PORT
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "doublenumerique-yann")
REGION = os.getenv("GOOGLE_CLOUD_REGION", "europe-west1")

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Configuration GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "yannabadie")
GITHUB_REPO = os.getenv("GITHUB_REPO", "appia-dev")

# Configuration Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# Models
class ChatMessage(BaseModel):
    message: str
    sender: str = "orchestrator"
    timestamp: Optional[str] = None


class TaskSuggestion(BaseModel):
    title: str
    description: str
    priority: int = 3  # 1=high, 2=medium, 3=low
    category: str = "general"
    metadata: Dict


class SystemStatus(BaseModel):
    status: str
    uptime: str
    last_activity: str
    active_tasks: int
    processed_messages: int


# Initialize FastAPI
app = FastAPI(
    title="JARVYS Orchestrator GCP",
    description="Orchestrateur autonome pour Google Cloud Platform",
    version="3.0.0",
)

# CORS pour dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier domaines exacts
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase: Client
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase client initialisé")
else:
    logger.warning("⚠️ Configuration Supabase manquante")

# Global state
orchestrator_state = {
    "startup_time": datetime.now(),
    "processed_messages": 0,
    "active_tasks": 0,
    "last_activity": datetime.now(),
    "connected_dashboards": 0,
    "github_sync_status": "initializing",
}

# GitHub sync manager
github_sync: GitHubSyncManager


# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        orchestrator_state["connected_dashboards"] = len(self.active_connections)
        logger.info(f"🔌 Dashboard connecté. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            orchestrator_state["connected_dashboards"] = len(self.active_connections)
            logger.info(
                f"🔌 Dashboard déconnecté. Total: {len(self.active_connections)}"
            )

    async def broadcast(self, message: dict):
        """Broadcast message to all connected dashboards"""
        if not self.active_connections:
            return

        for connection in self.active_connections[
            :
        ]:  # Copy to avoid modification during iteration
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ Erreur broadcast: {e}")
                self.disconnect(connection)


manager = ConnectionManager()


# Utility functions
def get_uptime():
    """Calcule l'uptime de l'orchestrateur"""
    uptime_seconds = (
        datetime.now() - orchestrator_state["startup_time"]
    ).total_seconds()
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    return f"{hours}h{minutes}m"


async def log_activity(activity: str, details: Dict):
    """Log une activité avec persistance Supabase"""
    try:
        orchestrator_state["last_activity"] = datetime.now()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "details": details or {},
            "orchestrator_id": f"gcp-{PROJECT_ID}",
            "uptime": get_uptime(),
        }

        # Log local
        logger.info(f"📝 {activity}: {details}")

        # Persistance Supabase si disponible
        if supabase:
            try:
                supabase.table("orchestrator_logs").insert(log_entry).execute()
            except Exception as e:
                logger.error(f"❌ Erreur Supabase log: {e}")

        # Broadcast aux dashboards
        await manager.broadcast({"type": "activity_log", "data": log_entry})

    except Exception as e:
        logger.error(f"❌ Erreur log_activity: {e}")


async def process_chat_message(message: str, sender: str = "user") -> str:
    """Traite un message de chat et génère une réponse"""
    try:
        orchestrator_state["processed_messages"] += 1

        await log_activity(
            "chat_message_received",
            {
                "message": message[:100] + "..." if len(message) > 100 else message,
                "sender": sender,
            },
        )

        # Simulation d'intelligence (remplacer par vraie IA)
        if "status" in message.lower():
            response = f"🤖 JARVYS Status: Actif depuis {get_uptime()}, {orchestrator_state['processed_messages']} messages traités."
        elif "task" in message.lower():
            response = f"🎯 {orchestrator_state['active_tasks']} tâches actives. Prêt pour nouvelles instructions."
        elif "help" in message.lower():
            response = "🆘 Commandes: 'status' (état), 'task' (tâches), 'analyze' (analyse repo)"
        else:
            response = f"🤖 Message reçu: '{message}'. Je suis JARVYS, votre orchestrateur autonome sur GCP. Comment puis-je vous aider?"

        # Stocker la réponse dans Supabase
        if supabase:
            try:
                chat_data = {
                    "message": response,
                    "sender": "orchestrator",
                    "timestamp": datetime.now().isoformat(),
                    "type": "orchestrator_response",
                    "metadata": {
                        "uptime": get_uptime(),
                        "processed_count": orchestrator_state["processed_messages"],
                    },
                }
                supabase.table("orchestrator_chat").insert(chat_data).execute()
            except Exception as e:
                logger.error(f"❌ Erreur chat Supabase: {e}")

        await log_activity("chat_response_sent", {"response_length": len(response)})
        return response

    except Exception as e:
        logger.error(f"❌ Erreur process_chat_message: {e}")
        return f"❌ Erreur lors du traitement: {str(e)}"


async def analyze_repository():
    """Analyse le repository GitHub et génère des suggestions"""
    try:
        orchestrator_state["active_tasks"] += 1

        await log_activity(
            "repository_analysis_start", {"repo": f"{GITHUB_OWNER}/{GITHUB_REPO}"}
        )

        # Simulation d'analyse (remplacer par vraie analyse)
        suggestions = [
            {
                "title": "Optimisation Docker",
                "description": "Optimiser les Dockerfiles pour réduire la taille des images",
                "priority": 2,
                "category": "infrastructure",
            },
            {
                "title": "Tests automatisés",
                "description": "Ajouter des tests unitaires pour les nouvelles fonctionnalités",
                "priority": 1,
                "category": "quality",
            },
            {
                "title": "Documentation API",
                "description": "Mettre à jour la documentation des endpoints",
                "priority": 3,
                "category": "documentation",
            },
        ]

        # Stocker suggestions dans Supabase
        if supabase:
            for suggestion in suggestions:
                try:
                    suggestion_data = {
                        **suggestion,
                        "timestamp": datetime.now().isoformat(),
                        "status": "pending",
                        "orchestrator_id": f"gcp-{PROJECT_ID}",
                    }
                    supabase.table("orchestrator_suggestions").insert(
                        suggestion_data
                    ).execute()
                except Exception as e:
                    logger.error(f"❌ Erreur suggestion Supabase: {e}")

        # Broadcast aux dashboards
        await manager.broadcast(
            {
                "type": "new_suggestions",
                "data": {"count": len(suggestions), "suggestions": suggestions},
            }
        )

        orchestrator_state["active_tasks"] -= 1
        await log_activity(
            "repository_analysis_complete", {"suggestions_count": len(suggestions)}
        )

        return suggestions

    except Exception as e:
        orchestrator_state["active_tasks"] -= 1
        logger.error(f"❌ Erreur analyze_repository: {e}")
        return []


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "JARVYS Orchestrator GCP",
        "version": "3.0.0",
        "status": "active",
        "uptime": get_uptime(),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check pour Cloud Run"""
    return {
        "status": "healthy",
        "uptime": get_uptime(),
        "active_connections": len(manager.active_connections),
        "last_activity": orchestrator_state["last_activity"].isoformat(),
    }


@app.get("/status")
async def get_status():
    """Récupère l'état complet de l'orchestrateur"""
    return {
        "timestamp": datetime.now().isoformat(),
        "orchestrator": {
            "status": "running",
            "uptime": get_uptime(),
            "processed_messages": orchestrator_state["processed_messages"],
            "active_tasks": orchestrator_state["active_tasks"],
            "last_activity": orchestrator_state["last_activity"].isoformat(),
            "project_id": PROJECT_ID,
            "region": REGION,
        },
        "connections": {
            "active_dashboards": len(manager.active_connections),
            "supabase_connected": supabase is not None,
        },
        "configuration": {
            "github_configured": bool(GITHUB_TOKEN),
            "anthropic_configured": bool(ANTHROPIC_API_KEY),
        },
    }


@app.post("/chat")
async def handle_chat(message: ChatMessage):
    """Traite un message de chat"""
    try:
        response = await process_chat_message(message.message, message.sender)

        # Broadcast to connected dashboards
        await manager.broadcast(
            {
                "type": "chat_message",
                "data": {
                    "message": message.message,
                    "sender": message.sender,
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ Erreur handle_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def trigger_analysis():
    """Lance une analyse du repository"""
    try:
        suggestions = await analyze_repository()
        return {"success": True, "suggestions": suggestions, "count": len(suggestions)}
    except Exception as e:
        logger.error(f"❌ Erreur trigger_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/suggestions")
async def get_suggestions():
    """Récupère les suggestions actives"""
    try:
        if not supabase:
            return {"suggestions": []}

        result = (
            supabase.table("orchestrator_suggestions")
            .select("*")
            .eq("status", "pending")
            .order("timestamp", desc=True)
            .limit(20)
            .execute()
        )

        return {"suggestions": result.data}
    except Exception as e:
        logger.error(f"❌ Erreur get_suggestions: {e}")
        return {"suggestions": []}


@app.get("/github/sync-status")
async def get_github_sync_status():
    """Récupère l'état de synchronisation GitHub"""
    try:
        if not github_sync:
            return {"status": "not_initialized"}

        return await github_sync.create_sync_dashboard_endpoint()
    except Exception as e:
        logger.error(f"❌ Erreur sync status: {e}")
        return {"status": "error", "error": str(e)}


@app.post("/github/apply-modification")
async def apply_github_modification(modification: dict):
    """Applique une modification GitHub depuis GCP"""
    try:
        if not github_sync:
            raise HTTPException(status_code=500, detail="GitHub sync not initialized")

        success = await github_sync.apply_gcp_modification(modification)

        if success:
            # Log l'activité
            await log_activity(
                "github_modification_applied",
                {
                    "type": modification.get("type"),
                    "files": modification.get("files", []),
                },
            )

            # Broadcast aux dashboards
            await manager.broadcast(
                {"type": "github_modification", "data": modification}
            )

            return {"success": True, "message": "Modification appliquée avec succès"}
        else:
            raise HTTPException(
                status_code=500, detail="Échec application modification"
            )

    except Exception as e:
        logger.error(f"❌ Erreur application modification GitHub: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour communication temps réel"""
    await manager.connect(websocket)
    try:
        # Envoyer l'état initial
        status = await get_status()
        await websocket.send_json({"type": "initial_status", "data": status})

        await log_activity(
            "dashboard_connected",
            {"total_connections": len(manager.active_connections)},
        )

        # Boucle de réception des messages
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "chat":
                message = data.get("message", "")
                response = await process_chat_message(message, "dashboard_user")
                await websocket.send_json(
                    {"type": "chat_response", "data": {"response": response}}
                )
            elif data.get("type") == "request_analysis":
                await trigger_analysis()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await log_activity(
            "dashboard_disconnected",
            {"total_connections": len(manager.active_connections)},
        )


# Background tasks
async def background_monitor():
    """Surveillance en arrière-plan"""
    while True:
        try:
            await asyncio.sleep(60)  # Toutes les minutes

            # Status broadcast
            status = await get_status()
            await manager.broadcast({"type": "status_update", "data": status})

            # Auto-analysis toutes les 30 minutes
            if datetime.now().minute % 30 == 0:
                await analyze_repository()

        except Exception as e:
            logger.error(f"❌ Erreur background_monitor: {e}")


async def check_pending_messages():
    """Vérifie les messages en attente dans Supabase"""
    if not supabase:
        return

    try:
        # Récupérer messages non traités
        result = (
            supabase.table("orchestrator_chat")
            .select("*")
            .eq("status", "pending")
            .eq("type", "user_to_orchestrator")
            .order("timestamp", desc=False)
            .limit(10)
            .execute()
        )

        for message_data in result.data:
            try:
                # Traiter le message
                response = await process_chat_message(
                    message_data["message"], message_data["sender"]
                )

                # Marquer comme traité
                supabase.table("orchestrator_chat").update({"status": "processed"}).eq(
                    "id", message_data["id"]
                ).execute()

                # Broadcast la réponse
                await manager.broadcast(
                    {
                        "type": "chat_response",
                        "data": {
                            "original_message": message_data["message"],
                            "response": response,
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                )

            except Exception as e:
                logger.error(
                    f"❌ Erreur traitement message {message_data.get('id')}: {e}"
                )

    except Exception as e:
        logger.error(f"❌ Erreur check_pending_messages: {e}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    global github_sync

    logger.info("🚀 JARVYS Orchestrator GCP démarré")
    logger.info(f"📍 Projet: {PROJECT_ID}, Région: {REGION}")
    logger.info(f"🔌 Port: {PORT}")

    await log_activity(
        "orchestrator_startup",
        {
            "project_id": PROJECT_ID,
            "region": REGION,
            "port": PORT,
            "supabase_configured": supabase is not None,
        },
    )

    # Initialiser la synchronisation GitHub
    try:
        github_sync = await setup_github_sync(orchestrator_state)
        if github_sync:
            orchestrator_state["github_sync_status"] = "active"
            logger.info("✅ Synchronisation GitHub initialisée")
        else:
            orchestrator_state["github_sync_status"] = "error"
            logger.warning("⚠️ Synchronisation GitHub non disponible")
    except Exception as e:
        logger.error(f"❌ Erreur init GitHub sync: {e}")
        orchestrator_state["github_sync_status"] = "error"

    # Démarrer les tâches en arrière-plan
    asyncio.create_task(background_monitor())

    # Vérifier les messages en attente toutes les 30 secondes
    async def message_checker():
        while True:
            await asyncio.sleep(30)
            await check_pending_messages()

    asyncio.create_task(message_checker())


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    await log_activity(
        "orchestrator_shutdown",
        {
            "uptime": get_uptime(),
            "processed_messages": orchestrator_state["processed_messages"],
        },
    )
    logger.info("👋 JARVYS Orchestrator GCP arrêté")


# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"📡 Signal {signum} reçu, arrêt gracieux...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("🎯 Démarrage JARVYS Orchestrator GCP")
    logger.info(f"🌐 Port: {PORT}")
    logger.info(f"📊 Supabase: {'✅ Connecté' if supabase else '❌ Non configuré'}")
    logger.info(f"🐙 GitHub: {'✅ Configuré' if GITHUB_TOKEN else '❌ Non configuré'}")

    # Configuration serveur Cloud Run
    uvicorn.run(
        "grok_orchestrator_gcp:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,  # Pas de reload en production
        log_level="info",
        access_log=True,
    )
