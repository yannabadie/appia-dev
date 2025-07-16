"""
🎯 JARVYS Command Interface
==========================

Interface de communication avec l'orchestrateur GROK pour le dashboard cloud.
Permet la communication bidirectionnelle, la validation des tâches et la gestion des priorités.

Architecture:
- API REST pour le dashboard cloud
- WebSocket pour communication temps réel
- Queue system pour tâches et validations
- Interface avec Supabase pour persistance

Usage:
    # Démarrer l'interface
    python jarvys_command_interface.py

    # API Endpoints:
    GET  /status          -> État orchestrateur
    GET  /logs            -> Logs temps réel
    POST /chat            -> Envoyer message à l'orchestrateur
    POST /validate        -> Valider/rejeter une suggestion
    GET  /suggestions     -> Liste des suggestions en attente
    POST /priority        -> Définir priorité d'une tâche
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import List, Optional

import psutil
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from supabase import Client, create_client

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ORCHESTRATOR_PID_FILE = "/tmp/grok_orchestrator.pid"
ORCHESTRATOR_LOG_FILE = "/workspaces/appia-dev/orchestrator_v2.log"


# Models
class ChatMessage(BaseModel):
    message: str
    timestamp: Optional[str] = None
    user_id: Optional[str] = "dashboard"


class TaskValidation(BaseModel):
    task_id: str
    action: str  # "approve", "reject", "defer"
    priority: int = 3  # 1=high, 2=medium, 3=low
    comment: Optional[str] = None


class PriorityUpdate(BaseModel):
    task_id: str
    priority: int
    notes: Optional[str] = None


# Initialize FastAPI
app = FastAPI(
    title="JARVYS Command Interface",
    description="Interface de communication avec l'orchestrateur GROK",
    version="2.0.0",
)

# CORS pour dashboard cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier le domaine du dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None


# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(
            f"🔌 Dashboard connecté. Connexions actives: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(
            f"🔌 Dashboard déconnecté. Connexions actives: {len(self.active_connections)}"
        )

    async def broadcast(self, message: dict):
        """Broadcast message to all connected dashboards"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.disconnect(connection)


manager = ConnectionManager()


# Utility functions
def get_orchestrator_status():
    """Récupère l'état de l'orchestrateur"""
    try:
        # Chercher le processus grok_orchestrator
        for proc in psutil.process_iter(
            ["pid", "name", "cmdline", "cpu_percent", "memory_info"]
        ):
            try:
                if proc.info["cmdline"] and any(
                    "grok_orchestrator.py" in cmd for cmd in proc.info["cmdline"]
                ):
                    return {
                        "status": "running",
                        "pid": proc.info["pid"],
                        "cpu_percent": proc.info["cpu_percent"],
                        "memory_mb": round(
                            proc.info["memory_info"].rss / 1024 / 1024, 1
                        ),
                        "uptime": get_process_uptime(proc.info["pid"]),
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {"status": "stopped", "pid": None}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_process_uptime(pid):
    """Calcule l'uptime du processus"""
    try:
        proc = psutil.Process(pid)
        create_time = proc.create_time()
        uptime_seconds = time.time() - create_time

        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)

        return f"{hours}h{minutes}m"
    except:
        return "unknown"


def get_recent_logs(lines=50):
    """Récupère les logs récents de l'orchestrateur"""
    try:
        if os.path.exists(ORCHESTRATOR_LOG_FILE):
            with open(ORCHESTRATOR_LOG_FILE, "r") as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        return []
    except Exception as e:
        return [f"Error reading logs: {str(e)}"]


def get_github_activity():
    """Récupère l'activité GitHub récente"""
    try:
        # Parse local_logs.json pour extraire l'activité récente
        logs_file = "/workspaces/appia-dev/local_logs.json"
        if os.path.exists(logs_file):
            with open(logs_file, "r") as f:
                logs = [
                    json.loads(line) for line in f.readlines()[-10:] if line.strip()
                ]

            return {
                "recent_commits": len(
                    [log for log in logs if log.get("action") == "commit"]
                ),
                "recent_tasks": len([log for log in logs if "task" in log]),
                "last_activity": logs[-1].get("timestamp") if logs else None,
            }
    except:
        pass

    return {"recent_commits": 0, "recent_tasks": 0, "last_activity": None}


# API Endpoints
@app.get("/")
async def root():
    return {"message": "JARVYS Command Interface v2.0", "status": "active"}


@app.get("/status")
async def get_status():
    """Récupère l'état complet de l'orchestrateur"""
    orchestrator_status = get_orchestrator_status()
    github_activity = get_github_activity()

    return {
        "timestamp": datetime.now().isoformat(),
        "orchestrator": orchestrator_status,
        "github": github_activity,
        "interface": {
            "status": "running",
            "connected_dashboards": len(manager.active_connections),
        },
    }


@app.get("/logs")
async def get_logs():
    """Récupère les logs récents"""
    logs = get_recent_logs()
    return {"logs": logs, "count": len(logs), "timestamp": datetime.now().isoformat()}


@app.post("/chat")
async def send_chat_message(message: ChatMessage):
    """Envoie un message à l'orchestrateur via Supabase"""
    try:
        if not supabase:
            return JSONResponse({"error": "Supabase not configured"}, status_code=500)

        # Stocker le message dans Supabase pour que l'orchestrateur le lise
        chat_data = {
            "message": message.message,
            "sender": message.user_id,
            "timestamp": message.timestamp or datetime.now().isoformat(),
            "type": "user_to_orchestrator",
            "status": "pending",
        }

        result = supabase.table("orchestrator_chat").insert(chat_data).execute()

        # Broadcast to connected dashboards
        await manager.broadcast({"type": "chat_sent", "data": chat_data})

        return {"success": True, "message_id": result.data[0]["id"]}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/validate")
async def validate_task(validation: TaskValidation):
    """Valide ou rejette une suggestion de l'orchestrateur"""
    try:
        if not supabase:
            return JSONResponse({"error": "Supabase not configured"}, status_code=500)

        # Mettre à jour le statut de la tâche dans Supabase
        validation_data = {
            "task_id": validation.task_id,
            "action": validation.action,
            "priority": validation.priority,
            "comment": validation.comment,
            "timestamp": datetime.now().isoformat(),
            "validator": "dashboard_user",
        }

        result = supabase.table("task_validations").insert(validation_data).execute()

        # Broadcast to orchestrator and dashboards
        await manager.broadcast({"type": "task_validated", "data": validation_data})

        return {"success": True, "validation_id": result.data[0]["id"]}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/suggestions")
async def get_pending_suggestions():
    """Récupère les suggestions en attente de validation"""
    try:
        if not supabase:
            return {"suggestions": []}

        # Récupérer les suggestions non validées
        result = (
            supabase.table("orchestrator_suggestions")
            .select("*")
            .eq("status", "pending")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )

        return {"suggestions": result.data}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/priority")
async def update_priority(priority_update: PriorityUpdate):
    """Met à jour la priorité d'une tâche"""
    try:
        if not supabase:
            return JSONResponse({"error": "Supabase not configured"}, status_code=500)

        # Mettre à jour la priorité
        result = (
            supabase.table("task_priorities")
            .upsert(
                {
                    "task_id": priority_update.task_id,
                    "priority": priority_update.priority,
                    "notes": priority_update.notes,
                    "updated_at": datetime.now().isoformat(),
                }
            )
            .execute()
        )

        # Broadcast the update
        await manager.broadcast(
            {
                "type": "priority_updated",
                "data": {
                    "task_id": priority_update.task_id,
                    "priority": priority_update.priority,
                    "notes": priority_update.notes,
                },
            }
        )

        return {"success": True}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour communication temps réel avec le dashboard"""
    await manager.connect(websocket)
    try:
        # Envoyer l'état initial
        status = await get_status()
        await websocket.send_json({"type": "initial_status", "data": status})

        # Boucle de réception des messages
        while True:
            data = await websocket.receive_json()

            # Traiter les différents types de messages
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "request_status":
                status = await get_status()
                await websocket.send_json({"type": "status_update", "data": status})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Background task pour monitoring
async def background_monitoring():
    """Tâche en arrière-plan pour surveiller l'orchestrateur"""
    while True:
        try:
            # Vérifier l'état toutes les 30 secondes
            await asyncio.sleep(30)

            status = get_orchestrator_status()

            # Broadcast status update to all connected dashboards
            await manager.broadcast(
                {
                    "type": "status_update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "orchestrator": status,
                    },
                }
            )

        except Exception as e:
            print(f"❌ Erreur monitoring: {e}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    print("🚀 JARVYS Command Interface démarrée")
    print(f"📊 Supabase: {'✅ Connecté' if supabase else '❌ Non configuré'}")

    # Démarrer le monitoring en arrière-plan
    asyncio.create_task(background_monitoring())


if __name__ == "__main__":
    # Configuration serveur
    port = int(os.getenv("PORT", 8000))

    print(f"🎯 Démarrage JARVYS Command Interface sur port {port}")
    print("📡 Endpoints disponibles:")
    print("   - GET  /status     -> État orchestrateur")
    print("   - GET  /logs       -> Logs temps réel")
    print("   - POST /chat       -> Chat avec orchestrateur")
    print("   - POST /validate   -> Validation tâches")
    print("   - GET  /suggestions-> Suggestions en attente")
    print("   - WS   /ws         -> WebSocket temps réel")

    uvicorn.run(
        "jarvys_command_interface:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Pas de reload en production
        log_level="info",
    )
