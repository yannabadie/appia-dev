#!/usr/bin/env python3
"""
🔧 Quick Fixes pour JARVYS_DEV - Implémentation des correctifs prioritaires
"""

from pathlib import Path


class JarvysDevQuickFixes:
    def __init__(self):
        self.workspace = Path("/workspaces/appia-dev")

    def fix_branch_to_main(self):
        """Fix 1: Modifier pour utiliser la branche main par défaut"""
        print("🔧 Fix 1: Configuration branche main par défaut")

        # 1. Modifier bootstrap_jarvys_dev.py
        bootstrap_file = self.workspace / "bootstrap_jarvys_dev.py"
        if bootstrap_file.exists():
            content = bootstrap_file.read_text()

            # Remplacer les références à 'dev' par 'main'
            content = content.replace('branch="dev"', 'branch="main"')
            content = content.replace("'dev'", "'main'")
            content = content.replace('"dev"', '"main"')

            # Modifier _check_branch pour accepter main
            if "_check_branch" in content:
                content = content.replace(
                    'expected_branch = "dev"',
                    'expected_branch = os.environ.get("JARVYS_TARGET_BRANCH", "main")',
                )

            bootstrap_file.write_text(content)
            print("✅ bootstrap_jarvys_dev.py mis à jour pour main")

        # 2. Modifier github_tools.py si nécessaire
        github_tools = self.workspace / "src/jarvys_dev/tools/github_tools.py"
        if github_tools.exists():
            content = github_tools.read_text()

            # Changer la branche par défaut dans create_pull_request
            if 'base="dev"' in content:
                content = content.replace('base="dev"', 'base="main"')

            if 'base_branch = "dev"' in content:
                content = content.replace('base_branch = "dev"', 'base_branch = "main"')

            github_tools.write_text(content)
            print("✅ github_tools.py mis à jour pour main")

    def fix_jarvys_ai_label(self):
        """Fix 2: Corriger le label des issues JARVYS_AI"""
        print("🔧 Fix 2: Correction label issues JARVYS_AI")

        main_file = self.workspace / "src/jarvys_dev/main.py"
        if main_file.exists():
            content = main_file.read_text()

            # Remplacer "from_jarvys_ai" par "from_jarvys_dev"
            content = content.replace(
                'label="from_jarvys_ai"', 'label="from_jarvys_dev"'
            )
            content = content.replace('"from_jarvys_ai"', '"from_jarvys_dev"')

            main_file.write_text(content)
            print("✅ Label d'issue corrigé: from_jarvys_ai → from_jarvys_dev")

    def add_pause_resume_functionality(self):
        """Fix 3: Ajouter fonctionnalité pause/reprise"""
        print("🔧 Fix 3: Ajout contrôle pause/reprise")

        # Créer un module de contrôle d'agent
        control_module = """#!/usr/bin/env python3
'''
🎛️ Agent Control Module for JARVYS_DEV
Contrôle de pause/reprise de l'agent autonome
'''

import asyncio
import logging
from typing import Dict, Any
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentController:
    '''Contrôleur pour pause/reprise de l'agent'''
    
    def __init__(self, _supabase_client =None):
        self.supabase = supabase_client
        self.is_paused = False
        self.pause_reason = ""
        
    async def check_pause_status(self) -> bool:
        '''Vérifier si l'agent doit être en pause'''
        try:
            if self.supabase:
                # Vérifier le statut dans Supabase
                _result = self.supabase.table('jarvys_agents_status').select('*').eq('agent_id', 'jarvys_dev_cloud').single().execute()
                
                if result.data:
                    status = result.data.get('status', 'active')
                    self.is_paused = (status == 'paused')
                    if self.is_paused:
                        self.pause_reason = result.data.get('pause_reason', 'Manual pause')
                        logger = logging.getLogger(__name__).info(f"🛑 Agent en pause: {self.pause_reason}")
                        return True
            
            # Vérifier variable d'environnement locale
            if os.environ.get('JARVYS_PAUSED', '').lower() == 'true':
                self.is_paused = True
                self.pause_reason = "Environment variable JARVYS_PAUSED=true"
                logger = logging.getLogger(__name__).info(f"🛑 Agent en pause: {self.pause_reason}")
                return True
            
            self.is_paused = False
            return False
            
        except Exception as e:
            logger = logging.getLogger(__name__).warning(f"⚠️ Erreur vérification pause: {e}")
            return False
    
    async def pause_agent(self, reason: str = "Manual pause") -> bool:
        '''Mettre l'agent en pause'''
        try:
            self.is_paused = True
            self.pause_reason = reason
            
            if self.supabase:
                # Mettre à jour le statut dans Supabase
                self.supabase.table('jarvys_agents_status').upsert({
                    'agent_id': 'jarvys_dev_cloud',
                    'status': 'paused',
                    'pause_reason': reason,
                    'last_updated': datetime.now().isoformat()
                }).execute()
            
            logger = logging.getLogger(__name__).info(f"🛑 Agent mis en pause: {reason}")
            return True
            
        except Exception as e:
            logger = logging.getLogger(__name__).error(f"❌ Erreur mise en pause: {e}")
            return False
    
    async def resume_agent(self) -> bool:
        '''Reprendre l'exécution de l'agent'''
        try:
            self.is_paused = False
            self.pause_reason = ""
            
            if self.supabase:
                # Mettre à jour le statut dans Supabase
                self.supabase.table('jarvys_agents_status').upsert({
                    'agent_id': 'jarvys_dev_cloud',
                    'status': 'active',
                    'pause_reason': None,
                    'last_updated': datetime.now().isoformat()
                }).execute()
            
            logger = logging.getLogger(__name__).info("▶️ Agent repris")
            return True
            
        except Exception as e:
            logger = logging.getLogger(__name__).error(f"❌ Erreur reprise: {e}")
            return False
    
    def should_continue_execution(self) -> bool:
        '''Vérifier si l'exécution peut continuer'''
        return not self.is_paused

# Instance globale pour contrôle d'agent
agent_controller = AgentController()

async def check_and_wait_if_paused():
    '''Vérifier et attendre si l'agent est en pause'''
    await agent_controller.check_pause_status()
    
    while agent_controller.is_paused:
        logger = logging.getLogger(__name__).info(f"⏸️ Agent en pause: {agent_controller.pause_reason}")
        logger = logging.getLogger(__name__).info("⏳ Attente de reprise... (vérification dans 60s)")
        await asyncio.sleep(60)
        await agent_controller.check_pause_status()
    
    return True
"""

        control_file = self.workspace / "src/jarvys_dev/agent_control.py"
        control_file.write_text(control_module)
        print("✅ Module de contrôle d'agent créé")

    def add_embeddings_to_memory_api(self):
        """Fix 4: Ajouter calcul d'embeddings à l'API mémoire"""
        print("🔧 Fix 4: Ajout embeddings à l'API mémoire")

        # Ajouter fonction d'embedding dans dashboard

        # Créer patch pour l'Edge Function dashboard
        patch_content = """
/* 
🔧 PATCH pour ajouter embeddings à l'API mémoire
À intégrer dans supabase/functions/jarvys-dashboard/index.ts
*/

{embedding_function}

/* 
Modifier l'endpoint /api/memory pour inclure:

if (url.pathname === '/api/memory' && request.method === 'POST') {{
  const body = await request.json();
  const {{ content, type = 'user_interaction' }} = body;
  
  // Calculer l'embedding
  const embedding = await calculateEmbedding(content);
  
  // Insérer avec embedding
  const memoryData = {{
    content,
    type,
    embedding: embedding.length > 0 ? embedding : null,
    timestamp: new Date().toISOString(),
    agent_id: 'jarvys_dev_cloud'
  }};
  
  const {{ error }} = await supabase
    .from('jarvys_memory')
    .insert(memoryData);
    
  if (error) {{
    return new Response(JSON.stringify({{ error: error.message }}), {{ 
      status: 500,
      headers: {{ 'Content-Type': 'application/json' }}
    }});
  }}
  
  return new Response(JSON.stringify({{ success: true, embedding_length: embedding.length }}), {{
    headers: {{ 'Content-Type': 'application/json' }}
  }});
}}
*/
"""

        patch_file = self.workspace / "supabase_memory_embedding_patch.js"
        patch_file.write_text(patch_content)
        print("✅ Patch embeddings créé: supabase_memory_embedding_patch.js")

    def add_exception_logging_decorator(self):
        """Fix 5: Ajouter décorateur de logging d'exceptions"""
        print("🔧 Fix 5: Décorateur logging exceptions")

        decorator_module = """#!/usr/bin/env python3
'''
🛡️ Exception Logging Decorator for JARVYS_DEV
Capture unifiée des exceptions avec logging en base
'''

import asyncio
import logging
import traceback
import functools
from datetime import datetime
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

def log_exceptions(
    log_to_memory: bool = True,
    supabase_client: Optional[Any] = None,
    reraise: bool = True
):
    '''
    Décorateur pour capturer et logger = logging.getLogger(__name__) toutes les exceptions
    
    Args:
        log_to_memory: Si True, log dans la mémoire infinie Supabase
        supabase_client: Client Supabase pour logging en base
        reraise: Si True, relance l'exception après logging
    '''
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
                    'function': func.__name__,
                    'module': func.__module__,
                    'exception_type': type(e).__name__,
                    'exception_message': str(e),
                    'traceback': traceback.format_exc(),
                    'timestamp': datetime.now().isoformat(),
                    'args': str(args) if args else None,
                    'kwargs': str(kwargs) if kwargs else None
                }
                
                # Logger local
                logger = logging.getLogger(__name__).error(f"❌ Exception dans {func.__name__}: {e}")
                logger = logging.getLogger(__name__).debug(f"🔍 Détails: {exc_info}")
                
                # Logger en base si activé
                if log_to_memory and supabase_client:
                    try:
                        memory_entry = {
                            'content': f"Exception in {func.__name__}: {e}",
                            'type': 'system_error',
                            'metadata': exc_info,
                            'agent_id': 'jarvys_dev_cloud',
                            'timestamp': exc_info['timestamp']
                        }
                        
                        supabase_client.table('jarvys_memory').insert(memory_entry).execute()
                        logger = logging.getLogger(__name__).debug("📝 Exception loggée en base Supabase")
                        
                    except Exception as log_error:
                        logger = logging.getLogger(__name__).warning(f"⚠️ Erreur logging exception en base: {log_error}")
                
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
                    'function': func.__name__,
                    'module': func.__module__,
                    'exception_type': type(e).__name__,
                    'exception_message': str(e),
                    'traceback': traceback.format_exc(),
                    'timestamp': datetime.now().isoformat(),
                    'args': str(args) if args else None,
                    'kwargs': str(kwargs) if kwargs else None
                }
                
                logger = logging.getLogger(__name__).error(f"❌ Exception dans {func.__name__}: {e}")
                logger = logging.getLogger(__name__).debug(f"🔍 Détails: {exc_info}")
                
                if log_to_memory and supabase_client:
                    try:
                        memory_entry = {
                            'content': f"Exception in {func.__name__}: {e}",
                            'type': 'system_error',
                            'metadata': exc_info,
                            'agent_id': 'jarvys_dev_cloud',
                            'timestamp': exc_info['timestamp']
                        }
                        
                        supabase_client.table('jarvys_memory').insert(memory_entry).execute()
                        
                    except Exception as log_error:
                        logger = logging.getLogger(__name__).warning(f"⚠️ Erreur logging exception en base: {log_error}")
                
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
"""

        decorator_file = self.workspace / "src/jarvys_dev/utils/exception_logger.py"
        decorator_file.parent.mkdir(exist_ok=True)
        decorator_file.write_text(decorator_module)
        print("✅ Décorateur exception_logger créé")

    def externalize_model_config(self):
        """Fix 6: Externaliser la configuration des modèles"""
        print("🔧 Fix 6: Externalisation config = {} modèles")

        # Créer fichier de configuration des modèles
        model_config = {
            "models": {
                "gpt-4": {
                    "provider": "openai",
                    "context_length": 8192,
                    "cost_per_token": 0.00003,
                    "capabilities": [
                        "reasoning",
                        "code",
                        "analysis",
                        "creative",
                    ],
                    "performance_score": 0.95,
                    "reliability_score": 0.98,
                },
                "gpt-3.5-turbo": {
                    "provider": "openai",
                    "context_length": 4096,
                    "cost_per_token": 0.000002,
                    "capabilities": ["reasoning", "code", "analysis"],
                    "performance_score": 0.85,
                    "reliability_score": 0.95,
                },
                "claude-3-sonnet": {
                    "provider": "anthropic",
                    "context_length": 200000,
                    "cost_per_token": 0.000015,
                    "capabilities": [
                        "reasoning",
                        "code",
                        "analysis",
                        "creative",
                        "long_context",
                    ],
                    "performance_score": 0.92,
                    "reliability_score": 0.96,
                },
                "gemini-pro": {
                    "provider": "google",
                    "context_length": 30720,
                    "cost_per_token": 0.000001,
                    "capabilities": ["reasoning", "code", "analysis"],
                    "performance_score": 0.88,
                    "reliability_score": 0.93,
                },
            },
            "routing_rules": {
                "cost_optimization": True,
                "prefer_local": False,
                "fallback_chain": [
                    "gpt-4",
                    "claude-3-sonnet",
                    "gpt-3.5-turbo",
                ],
                "task_routing": {
                    "simple_queries": "gpt-3.5-turbo",
                    "complex_reasoning": "gpt-4",
                    "long_context": "claude-3-sonnet",
                    "cost_sensitive": "gemini-pro",
                },
            },
            "thresholds": {
                "confidence_threshold": 0.85,
                "cost_daily_limit": 3.0,
                "performance_min": 0.80,
            },
        }

        config_file = self.workspace / "src/jarvys_dev/model_capabilities.json"
        import json

        config_file.write_text(json.dumps(model_config, indent=2))
        print("✅ Configuration modèles externalisée: model_capabilities.json")

    def apply_all_fixes(self):
        """Appliquer tous les correctifs"""
        print("🚀 Application des Quick Fixes JARVYS_DEV")
        print("=" * 50)

        try:
            self.fix_branch_to_main()
            self.fix_jarvys_ai_label()
            self.add_pause_resume_functionality()
            self.add_embeddings_to_memory_api()
            self.add_exception_logging_decorator()
            self.externalize_model_config()

            print("\n✅ Tous les Quick Fixes appliqués avec succès!")
            print("\n📋 Récapitulatif:")
            print("  1. ✅ Branche par défaut: dev → main")
            print("  2. ✅ Label issues: from_jarvys_ai → from_jarvys_dev")
            print("  3. ✅ Contrôle pause/reprise ajouté")
            print("  4. ✅ Patch embeddings mémoire créé")
            print("  5. ✅ Décorateur exceptions créé")
            print("  6. ✅ Configuration modèles externalisée")

            return True

        except Exception as e:
            print(f"❌ Erreur lors de l'application des fixes: {e}")
            return False


def main():
    """Fonction principale"""
    fixes = JarvysDevQuickFixes()
    success = fixes.apply_all_fixes()

    if success:
        print("\n🎯 Actions suivantes recommandées:")
        print("  1. Commiter et pousser les changements")
        print("  2. Appliquer le patch embeddings dans Supabase Edge Function")
        print("  3. Tester la fonctionnalité pause/reprise via dashboard")
        print("  4. Valider la nouvelle configuration modèles")

        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
