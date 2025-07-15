#!/usr/bin/env python3
"""
🛡️ Exception Logging Decorator for JARVYS_DEV
Capture unifiée des exceptions avec logging en base
"""

import asyncio
import functools
import logging
import traceback
from datetime import datetime
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def log_exceptions(
    log_to_memory: bool = True,
    supabase_client: Optional[Any] = None,
    reraise: bool = True,
):
    """
    Décorateur pour capturer et logger toutes les exceptions

    Args:
        log_to_memory: Si True, log dans la mémoire infinie Supabase
        supabase_client: Client Supabase pour logging en base
        reraise: Si True, relance l'exception après logging
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                # Capturer les informations d'exception
                exc_info = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now().isoformat(),
                    "args": str(args) if args else None,
                    "kwargs": str(kwargs) if kwargs else None,
                }

                # Logger local
                logger.error(f"❌ Exception dans {func.__name__}: {e}")
                logger.debug(f"🔍 Détails: {exc_info}")

                # Logger en base si activé
                if log_to_memory and supabase_client:
                    try:
                        memory_entry = {
                            "content": f"Exception in {func.__name__}: {e}",
                            "type": "system_error",
                            "metadata": exc_info,
                            "agent_id": "jarvys_dev_cloud",
                            "timestamp": exc_info["timestamp"],
                        }

                        supabase_client.table("jarvys_memory").insert(
                            memory_entry
                        ).execute()
                        logger.debug("📝 Exception loggée en base Supabase")

                    except Exception as log_error:
                        logger.warning(
                            f"⚠️ Erreur logging exception en base: {log_error}"
                        )

                # Relancer l'exception si demandé
                if reraise:
                    raise
                else:
                    return None

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Même logique pour fonctions synchrones
                exc_info = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now().isoformat(),
                    "args": str(args) if args else None,
                    "kwargs": str(kwargs) if kwargs else None,
                }

                logger.error(f"❌ Exception dans {func.__name__}: {e}")
                logger.debug(f"🔍 Détails: {exc_info}")

                if log_to_memory and supabase_client:
                    try:
                        memory_entry = {
                            "content": f"Exception in {func.__name__}: {e}",
                            "type": "system_error",
                            "metadata": exc_info,
                            "agent_id": "jarvys_dev_cloud",
                            "timestamp": exc_info["timestamp"],
                        }

                        supabase_client.table("jarvys_memory").insert(
                            memory_entry
                        ).execute()

                    except Exception as log_error:
                        logger.warning(
                            f"⚠️ Erreur logging exception en base: {log_error}"
                        )

                if reraise:
                    raise
                else:
                    return None

        # Retourner le bon wrapper selon le type de fonction
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Exemple d'utilisation:
# @log_exceptions(log_to_memory=True, _supabase_client =supabase)
# async def ma_fonction():
#     # Code qui peut lever une exception
#     pass
