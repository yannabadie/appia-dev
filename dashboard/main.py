#!/usr/bin/env python3
"""
JARVYS_DEV Dashboard - Interface de monitoring et contrôle.
Dashboard interactif pour surveiller et interagir avec l'agent autonome.
"""

import asyncio
import json
import sqlite3
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Ajout du chemin src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from jarvys_dev.langgraph_loop import run_loop
    from jarvys_dev.multi_model_router import MultiModelRouter
    from jarvys_dev.tools.memory import memory_search
except ImportError as e:
    print(f"Erreur d'import JARVYS modules: {e}")


class JarvysMetrics:
    """Système de métriques pour JARVYS_DEV."""

    def __init__(self, db_path: str = "jarvys_metrics.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialise la base de données des métriques."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table des appels API
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_calls (
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                provider TEXT,
                model TEXT,
                tokens_input INTEGER,
                tokens_output INTEGER,
                cost_usd REAL,
                latency_ms REAL,
                success BOOLEAN,
                task_type TEXT
            )
        """
        )

        # Table des tâches
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                type TEXT,
                status TEXT,
                description TEXT,
                github_url TEXT,
                confidence_score REAL,
                duration_ms REAL
            )
        """
        )

        # Table des conversations
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                user_message TEXT,
                agent_response TEXT,
                context TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def log_api_call(
        self,
        provider: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost: float,
        latency: float,
        success: bool,
        task_type: str = "unknown",
    ):
        """Log un appel API."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO api_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                str(uuid.uuid4()),
                datetime.now(),
                provider,
                model,
                tokens_in,
                tokens_out,
                cost,
                latency,
                success,
                task_type,
            ),
        )

        conn.commit()
        conn.close()

    def log_task(
        self,
        task_type: str,
        status: str,
        description: str,
        github_url: str = None,
        confidence: float = None,
        duration: float = None,
    ):
        """Log une tâche."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                str(uuid.uuid4()),
                datetime.now(),
                task_type,
                status,
                description,
                github_url,
                confidence,
                duration,
            ),
        )

        conn.commit()
        conn.close()

    def log_conversation(self, user_msg: str, agent_response: str, context: str = ""):
        """Log une conversation avec l'agent."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO conversations VALUES (?, ?, ?, ?, ?)
        """,
            (
                str(uuid.uuid4()),
                datetime.now(),
                user_msg,
                agent_response,
                context,
            ),
        )

        conn.commit()
        conn.close()

    def get_api_costs_today(self) -> Dict[str, Any]:
        """Récupère les coûts API du jour."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().date()
        cursor.execute(
            """
            SELECT provider, SUM(cost_usd), COUNT(*), AVG(latency_ms)
            FROM api_calls 
            WHERE DATE(timestamp) = ?
            GROUP BY provider
        """,
            (today,),
        )

        results = cursor.fetchall()
        conn.close()

        return {
            "total_cost": sum(row[1] for row in results),
            "by_provider": {
                row[0]: {
                    "cost": row[1],
                    "calls": row[2],
                    "avg_latency": row[3],
                }
                for row in results
            },
        }

    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les tâches récentes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM tasks 
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (limit,),
        )

        columns = [
            "id",
            "timestamp",
            "type",
            "status",
            "description",
            "github_url",
            "confidence_score",
            "duration_ms",
        ]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results


class JarvysAgent:
    """Agent JARVYS avec métriques intégrées."""

    def __init__(self):
        self.router = MultiModelRouter()
        self.metrics = JarvysMetrics()
        self.active_tasks = []

    async def chat(self, user_message: str) -> str:
        """Chat interactif avec l'agent."""
        start_time = datetime.now()

        try:
            # Construire le contexte
            context = await self._build_context(user_message)

            # Générer la réponse
            prompt = """Tu es JARVYS_DEV, un agent DevOps autonome.
            
Contexte actuel:
{context}

Question de l'utilisateur: {user_message}

Réponds de manière conversationnelle et informative. Si la question concerne:
- Tes capacités: explique ce que tu peux faire
- Ton état: donne des métriques récentes
- Des améliorations: propose des idées concrètes
- Ton architecture: explique tes composants

Réponse:"""

            _response = self.router.generate(prompt, task_type="reasoning")

            # Log la conversation
            self.metrics.log_conversation(user_message, response, context)

            # Log l'appel API (approximatif)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.log_api_call(
                provider="openai",
                model="gpt-4o",
                tokens_in=len(prompt.split()) * 1.3,  # Approximation
                tokens_out=len(response.split()) * 1.3,
                cost=0.03 * (len(prompt) + len(response)) / 1000,  # Estimation
                latency=duration,
                success=True,
                task_type="chat",
            )

            return response

        except Exception as e:
            error_response = f"Désolé, j'ai rencontré une erreur: {str(e)}"
            self.metrics.log_conversation(
                user_message, error_response, f"ERROR: {str(e)}"
            )
            return error_response

    async def _build_context(self, message: str) -> str:
        """Construit le contexte pour la réponse."""
        context_parts = []

        # Métriques récentes
        costs = self.metrics.get_api_costs_today()
        context_parts.append(f"Coûts API aujourd'hui: ${costs['total_cost']:.4f}")

        # Tâches récentes
        recent_tasks = self.metrics.get_recent_tasks(3)
        if recent_tasks:
            context_parts.append("Tâches récentes:")
            for task in recent_tasks[:3]:
                context_parts.append(f"- {task['type']}: {task['status']}")

        # Recherche dans la mémoire si pertinent
        if len(message) > 10:
            try:
                memories = memory_search(message, k=2)
                if memories:
                    context_parts.append("Mémoires pertinentes:")
                    context_parts.extend(f"- {mem[:100]}..." for mem in memories[:2])
            except Exception:
                pass  # Mémoire non disponible

        return "\n".join(context_parts)

    async def execute_autonomous_loop(self):
        """Exécute une boucle autonome et log les métriques."""
        start_time = datetime.now()

        try:
            # Exécuter la boucle
            state = run_loop(steps=1)

            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Log la tâche
            self.metrics.log_task(
                task_type="autonomous_loop",
                status=(
                    "completed"
                    if not state.get("waiting_for_human_review")
                    else "needs_review"
                ),
                description=f"Loop executed: {state.get('plan', 'No plan')}",
                github_url=state.get("action_url"),
                confidence=(1.0 if not state.get("waiting_for_human_review") else 0.5),
                duration=duration,
            )

            return state

        except Exception as e:
            self.metrics.log_task(
                task_type="autonomous_loop",
                status="failed",
                description=f"Error: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds() * 1000,
            )
            raise

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Récupère les données pour le dashboard."""
        return {
            "costs": self.metrics.get_api_costs_today(),
            "recent_tasks": self.metrics.get_recent_tasks(5),
            "status": {
                "active": True,
                "version": "0.1.0",
                "uptime": "Running",
                "last_loop": datetime.now().isoformat(),
            },
        }


# Instance globale
jarvys = JarvysAgent()

# Application FastAPI
app = FastAPI(title="JARVYS_DEV Dashboard", version="0.1.0")

# Configuration des templates et fichiers statiques


@app.get("/")
async def root():
    """Point d'entrée principal - redirige vers le dashboard Supabase."""
    return {
        "service": "JARVYS_DEV Dashboard API",
        "version": "0.1.0",
        "status": "active",
        "dashboard_url": "Déployé sur Supabase Edge Functions",
        "secret_configured": True,
        "message": "Utilisez /api/status pour les métriques",
    }


@app.get("/api/status")
async def get_status():
    """API pour récupérer le statut de l'agent."""
    return jarvys.get_dashboard_data()


@app.post("/api/execute-loop")
async def execute_loop():
    """API pour déclencher une boucle autonome."""
    try:
        state = await jarvys.execute_autonomous_loop()
        return {"success": True, "state": state}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket pour le chat en temps réel."""
    await websocket.accept()

    try:
        while True:
            # Recevoir le message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")

            if user_message:
                # Générer la réponse
                _response = await jarvys.chat(user_message)

                # Envoyer la réponse
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "response",
                            "message": response,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

    except WebSocketDisconnect:
        pass


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket pour les métriques en temps réel."""
    await websocket.accept()

    try:
        while True:
            # Envoyer les métriques toutes les 5 secondes
            data = jarvys.get_dashboard_data()
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        pass


@app.get("/api/logs")
async def get_logs():
    """Récupère les logs récents du système."""
    try:
        # Lecture des logs depuis la base de données
        conn = sqlite3.connect("jarvys_metrics.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, service, status, endpoint, response_time_ms
            FROM api_calls 
            ORDER BY timestamp DESC LIMIT 100
        """
        )

        logs = []
        for row in cursor.fetchall():
            logs.append(
                {
                    "timestamp": row[0],
                    "service": row[1],
                    "status": row[2],
                    "endpoint": row[3] or "N/A",
                    "response_time": row[4],
                }
            )

        conn.close()
        return {"logs": logs}

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/agent/control")
async def control_agent(action: dict):
    """Contrôle l'agent (pause, redémarrage, etc.)."""
    try:
        action_type = action.get("action")

        if action_type == "pause":
            # TODO: Implémenter la pause de l'agent
            message = "Agent mis en pause"
        elif action_type == "restart":
            # TODO: Implémenter le redémarrage
            message = "Agent redémarré"
        elif action_type == "status":
            return {
                "status": "running",
                "uptime": "02:34:56",
                "last_task": "Documentation update",
            }
        else:
            return {"error": "Action non reconnue"}

        # Log l'action
        print(f"Action agent: {action_type} - {message}")

        return {"success": True, "message": message}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("🚀 Démarrage du Dashboard JARVYS_DEV...")
    print("📊 Interface disponible sur: http://localhost:8080")
    print("💬 Chat interactif intégré")
    print("📈 Métriques en temps réel")

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
