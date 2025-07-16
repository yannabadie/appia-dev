#!/usr/bin/env python3
"""
🎛️ Agent Control Module for JARVYS_DEV
Contrôle de pause/reprise de l'agent autonome
"""

import asyncio
import logging
import os
from datetime import datetime

<<<<<<< HEAD
from dotenv import load_dotenv

=======
>>>>>>> origin/main
logger = logging.getLogger(__name__)


class AgentController:
    """Contrôleur pour pause/reprise de l'agent"""

    def __init__(self, _supabase_client=None):
        self.supabase = _supabase_client
        self.is_paused = False
        self.pause_reason = ""

    async def check_pause_status(self) -> bool:
        """Vérifier si l'agent doit être en pause"""
        try:
            if self.supabase:
                # Vérifier le statut dans Supabase
                _result = (
                    self.supabase.table("jarvys_agents_status")
                    .select("*")
                    .eq("agent_id", "jarvys_dev_cloud")
                    .single()
                    .execute()
                )

                if _result.data:
                    status = _result.data.get("status", "active")
                    self.is_paused = status == "paused"
                    if self.is_paused:
                        self.pause_reason = _result.data.get(
                            "pause_reason", "Manual pause"
                        )
                        logger.info(f"🛑 Agent en pause: {self.pause_reason}")
                        return True

            # Vérifier variable d'environnement locale
            if os.environ.get("JARVYS_PAUSED", "").lower() == "true":
                self.is_paused = True
                self.pause_reason = "Environment variable JARVYS_PAUSED=true"
                logger.info(f"🛑 Agent en pause: {self.pause_reason}")
                return True

            self.is_paused = False
            return False

        except Exception as e:
            logger.warning(f"⚠️ Erreur vérification pause: {e}")
            return False

    async def pause_agent(self, reason: str = "Manual pause") -> bool:
        """Mettre l'agent en pause"""
        try:
            self.is_paused = True
            self.pause_reason = reason

            if self.supabase:
                # Mettre à jour le statut dans Supabase
                self.supabase.table("jarvys_agents_status").upsert(
                    {
                        "agent_id": "jarvys_dev_cloud",
                        "status": "paused",
                        "pause_reason": reason,
                        "last_updated": datetime.now().isoformat(),
                    }
                ).execute()

            logger.info(f"🛑 Agent mis en pause: {reason}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur mise en pause: {e}")
            return False

    async def resume_agent(self) -> bool:
        """Reprendre l'exécution de l'agent"""
        try:
            self.is_paused = False
            self.pause_reason = ""

            if self.supabase:
                # Mettre à jour le statut dans Supabase
                self.supabase.table("jarvys_agents_status").upsert(
                    {
                        "agent_id": "jarvys_dev_cloud",
                        "status": "active",
                        "pause_reason": None,
                        "last_updated": datetime.now().isoformat(),
                    }
                ).execute()

            logger.info("▶️ Agent repris")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur reprise: {e}")
            return False

    def should_continue_execution(self) -> bool:
        """Vérifier si l'exécution peut continuer"""
        return not self.is_paused


# Instance globale pour contrôle d'agent
agent_controller = AgentController()


async def check_and_wait_if_paused():
    """Vérifier et attendre si l'agent est en pause"""
    await agent_controller.check_pause_status()

    while agent_controller.is_paused:
        logger.info(f"⏸️ Agent en pause: {agent_controller.pause_reason}")
        logger.info("⏳ Attente de reprise... (vérification dans 60s)")
        await asyncio.sleep(60)
        await agent_controller.check_pause_status()

    return True
<<<<<<< HEAD


def route_to_grok(query):
    from grok_api import GrokClient

    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY not found in environment variables")

    client = GrokClient(api_key=api_key)
    return client.complete(query, model="grok-4")
=======
>>>>>>> origin/main
