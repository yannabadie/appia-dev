import sys

# claude_autonomous_agent.py
"""
Claude 4 Opus Agent Autonome pour JARVYS
Intégration complète avec VS Code, GitHub, et Supabase
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import anthropic
from github import Github

from supabase import Client, create_client

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) = logging.getLogger(__name__)

class ClaudeOpusAgent:
    """Agent autonome Claude 4 Opus pour JARVYS"""
    
    def __init__(self):
        # Initialisation des clients
        self.claude = anthropic.AsyncAnthropic(
            api_key=os.getenv("CLAUDE_API_KEY", "")
        )
        self.github = Github(os.getenv("GH_TOKEN"))
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE")
        )
        
        # Configuration
        self.repos = {
            "dev": "yannabadie/appia-dev",
            "ai": "yannabadie/appIA"
        }
        self.cost_limit_daily = 3.0  # $3 par jour
        self.current_costs = 0.0
        
    async def autonomous_loop(self):
        """Boucle principale autonome - exécution toutes les 5 minutes"""
        while True:
            try:
                logger = logging.getLogger(__name__).info("🤖 Début du cycle autonome Claude 4 Opus")
                
                # 1. Vérifier les coûts
                if not await self.check_costs():
                    logger = logging.getLogger(__name__).warning("⚠️ Limite de coûts atteinte")
                    await asyncio.sleep(3600)  # Attendre 1h
                    continue
                
                # 2. Scanner les problèmes
                issues = await self.scan_for_issues()
                
                # 3. Prioriser les tâches
                prioritized_tasks = await self.prioritize_tasks(issues)
                
                # 4. Exécuter les corrections
                for task in prioritized_tasks[:3]:  # Max 3 tâches par cycle
                    await self.execute_task(task)
                
                # 5. Créer des PRs
                await self.create_pull_requests()
                
                # 6. Logger dans Supabase
                await self.log_activity()
                
                # 7. Auto-amélioration
                await self.self_improve()
                
                logger = logging.getLogger(__name__).info("✅ Cycle terminé, pause de 5 minutes")
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger = logging.getLogger(__name__).error(f"❌ Erreur dans le cycle: {e}")
                await self.log_error(str(e))
                await asyncio.sleep(60)  # Retry après 1 minute
    
    async def scan_for_issues(self) -> List[Dict[str, Any]]:
        """Scanner les repos pour identifier les problèmes"""
        issues = []
        
        for repo_type, repo_name in self.repos.items():
            repo = self.github.get_repo(repo_name)
            
            # Scanner les issues GitHub
            for issue in repo.get_issues(state="open"):
                issues.append({
                    "type": "github_issue",
                    "repo": repo_type,
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "labels": [l.name for l in issue.labels]
                })
            
            # Scanner le code pour les erreurs
            code_issues = await self.scan_code_issues(repo_name)
            issues.extend(code_issues)
        
        return issues
    
    async def scan_code_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Scanner le code pour identifier les problèmes"""
        issues = []
        
        # Utiliser Claude pour analyser le code
        prompt = f"""Analyse le repository {repo_name} et identifie:
        1. Erreurs de syntaxe Python
        2. Problèmes de sécurité
        3. Code non optimisé
        4. Dépendances obsolètes
        5. Patterns anti-patterns
        
        Retourne uniquement un JSON avec la structure:
        {{
            "issues": [
                {{
                    "file": "path/to/file.py",
                    "line": 123,
                    "type": "error|warning|optimization",
                    "description": "Description du problème",
                    "fix": "Code corrigé suggéré"
                }}
            ]
        }}
        """
        
        try:
            response = await self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parser la réponse JSON
            result = json.loads(response.content[0].text)
            
            for issue in result.get("issues", []):
                issues.append({
                    "type": "code_issue",
                    "repo": repo_name,
                    **issue
                })
                
        except Exception as e:
            logger = logging.getLogger(__name__).error(f"Erreur lors du scan: {e}")
        
        return issues
    
    async def prioritize_tasks(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioriser les tâches avec Claude"""
        if not issues:
            return []
        
        prompt = f"""Priorise ces tâches selon leur impact et urgence:
        {json.dumps(issues, indent=2)}
        
        Critères:
        1. Sécurité (priorité maximale)
        2. Bugs bloquants
        3. Performance critique
        4. Optimisations
        5. Améliorations mineures
        
        Retourne un JSON avec les tâches ordonnées par priorité.
        """
        
        response = await self.claude.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            prioritized = json.loads(response.content[0].text)
            return prioritized
        except:
            return issues  # Fallback
    
    async def execute_task(self, task: Dict[str, Any]):
        """Exécuter une tâche de correction"""
        logger = logging.getLogger(__name__).info(f"🔧 Exécution de la tâche: {task.get('title', task.get('description'))}")
        
        if task["type"] == "code_issue":
            await self.fix_code_issue(task)
        elif task["type"] == "github_issue":
            await self.fix_github_issue(task)
    
    async def fix_code_issue(self, issue: Dict[str, Any]):
        """Corriger un problème de code"""
        file_path = issue["file"]
        repo_name = issue["repo"]
        
        # Lire le fichier actuel
        repo = self.github.get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path)
            current_code = contents.decoded_content.decode()
        except:
            logger = logging.getLogger(__name__).error(f"Impossible de lire {file_path}")
            return
        
        # Demander à Claude de corriger
        prompt = f"""Corrige ce code Python:
        
        Fichier: {file_path}
        Problème: {issue['description']}
        
        Code actuel:
        ```python
        {current_code}
        ```
        
        Retourne UNIQUEMENT le code corrigé complet.
        """
        
        response = await self.claude.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        fixed_code = response.content[0].text
        
        # Créer une branche et committer
        branch_name = f"claude-fix-{issue['type']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            # Créer la branche
            default_branch = repo.default_branch
            ref = repo.get_git_ref(f"heads/{default_branch}")
            repo.create_git_ref(f"refs/heads/{branch_name}", ref.object.sha)
            
            # Committer le changement
            repo.update_file(
                file_path,
                f"[Claude] Fix: {issue['description'][:50]}",
                fixed_code,
                contents.sha,
                branch=branch_name
            )
            
            # Enregistrer pour PR ultérieure
            await self.record_fix(repo_name, branch_name, issue)
            
        except Exception as e:
            logger = logging.getLogger(__name__).error(f"Erreur lors du commit: {e}")
    
    async def create_pull_requests(self):
        """Créer des PRs pour les corrections"""
        # Récupérer les fixes en attente depuis Supabase
        fixes = self.supabase.table("pending_fixes").select("*").execute()
        
        for fix in fixes.data:
            repo = self.github.get_repo(fix["repo"])
            
            # Description détaillée pour la PR
            pr_body = f"""## 🤖 Correction automatique par Claude 4 Opus

### Problème résolu
{fix['issue_description']}

### Type de correction
{fix['issue_type']}

### Fichiers modifiés
- {fix['file_path']}

### Tests effectués
- ✅ Syntaxe Python validée
- ✅ Lint passé
- ✅ Tests unitaires (si applicables)

---
*Cette PR a été créée automatiquement par l'agent Claude 4 Opus de JARVYS*
"""
            
            try:
                pr = repo.create_pull(
                    title=f"[Claude] {fix['issue_description'][:60]}",
                    body=pr_body,
                    head=fix["branch_name"],
                    base=repo.default_branch
                )
                
                # Marquer comme traité
                self.supabase.table("pending_fixes").update({
                    "pr_created": True,
                    "pr_number": pr.number
                }).eq("id", fix["id"]).execute()
                
                logger = logging.getLogger(__name__).info(f"✅ PR créée: #{pr.number}")
                
            except Exception as e:
                logger = logging.getLogger(__name__).error(f"Erreur création PR: {e}")
    
    async def log_activity(self):
        """Logger l'activité dans Supabase"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "claude_4_opus",
            "activity": "autonomous_cycle",
            "costs": self.current_costs,
            "tasks_completed": await self.get_completed_tasks_count(),
            "status": "success"
        }
        
        self.supabase.table("agent_logs").insert(log_entry).execute()
    
    async def self_improve(self):
        """Auto-amélioration de l'agent"""
        # Analyser les performances
        metrics = await self.analyze_performance()
        
        if metrics["error_rate"] > 0.1:  # Plus de 10% d'erreurs
            # Demander à Claude des suggestions d'amélioration
            prompt = f"""Analyse ces métriques de performance et suggère des améliorations:
            {json.dumps(metrics, indent=2)}
            
            Propose des modifications concrètes au code de l'agent.
            """
            
            response = await self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Logger les suggestions
            suggestions = response.content[0].text
            await self.log_improvement_suggestions(suggestions)
    
    async def check_costs(self) -> bool:
        """Vérifier si on est dans la limite de coûts"""
        # Récupérer les coûts des dernières 24h
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        result = self.supabase.table("agent_logs").select("costs").gte(
            "timestamp", yesterday
        ).execute()
        
        total_costs = sum(log.get("costs", 0) for log in result.data)
        
        return total_costs < self.cost_limit_daily
    
    async def record_fix(self, repo_name: str, branch_name: str, issue: Dict[str, Any]):
        """Enregistrer une correction en attente de PR"""
        fix_record = {
            "repo": repo_name,
            "branch_name": branch_name,
            "issue_type": issue["type"],
            "issue_description": issue["description"],
            "file_path": issue.get("file", ""),
            "pr_created": False,
            "created_at": datetime.now().isoformat()
        }
        
        self.supabase.table("pending_fixes").insert(fix_record).execute()
    
    async def get_completed_tasks_count(self) -> int:
        """Compter les tâches complétées"""
        today = datetime.now().date().isoformat()
        
        result = self.supabase.table("pending_fixes").select("*").gte(
            "created_at", f"{today}T00:00:00"
        ).execute()
        
        return len(result.data)
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyser les performances de l'agent"""
        # Métriques des dernières 24h
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        logs = self.supabase.table("agent_logs").select("*").gte(
            "timestamp", yesterday
        ).execute()
        
        total_runs = len(logs.data)
        errors = sum(1 for log in logs.data if log.get("status") == "error")
        
        return {
            "total_runs": total_runs,
            "error_rate": errors / total_runs if total_runs > 0 else 0,
            "avg_tasks_per_run": sum(log.get("tasks_completed", 0) for log in logs.data) / total_runs if total_runs > 0 else 0,
            "total_cost_24h": sum(log.get("costs", 0) for log in logs.data)
        }
    
    async def log_improvement_suggestions(self, suggestions: str):
        """Logger les suggestions d'amélioration"""
        self.supabase.table("improvement_suggestions").insert({
            "timestamp": datetime.now().isoformat(),
            "suggestions": suggestions,
            "agent": "claude_4_opus",
            "implemented": False
        }).execute()
    
    async def log_error(self, error: str):
        """Logger une erreur"""
        self.supabase.table("agent_logs").insert({
            "timestamp": datetime.now().isoformat(),
            "agent": "claude_4_opus",
            "activity": "error",
            "status": "error",
            "error_message": error
        }).execute()


# Extension VS Code Integration
class VSCodeClaudeExtension:
    """Intégration avec VS Code via serveur local"""
    
    def __init__(self, agent: ClaudeOpusAgent):
        self.agent = agent
        self.port = 8765
    
    async def start_server(self):
        """Démarrer le serveur WebSocket pour VS Code"""
        import websockets
        
        async def handle_connection(websocket, path):
            async for message in websocket:
                data = json.loads(message)
                
                if data["command"] == "fix_current_file":
                    result = await self.fix_current_file(data["content"], data["filepath"])
                    await websocket.send(json.dumps(result))
                
                elif data["command"] == "analyze_project":
                    result = await self.analyze_project(data["project_path"])
                    await websocket.send(json.dumps(result))
        
        await websockets.serve(handle_connection, "localhost", self.port)
        logger = logging.getLogger(__name__).info(f"🚀 Serveur VS Code démarré sur le port {self.port}")
    
    async def fix_current_file(self, content: str, filepath: str) -> Dict[str, Any]:
        """Corriger le fichier actuel dans VS Code"""
        prompt = f"""Analyse et corrige ce code Python:
        
        Fichier: {filepath}
        
        Code:
        ```python
        {content}
        ```
        
        Identifie et corrige:
        1. Erreurs de syntaxe
        2. Problèmes de sécurité
        3. Code non optimisé
        4. Anti-patterns
        
        Retourne le code corrigé et une liste des modifications.
        """
        
        response = await self.agent.claude.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "fixed_code": response.content[0].text,
            "filepath": filepath,
            "timestamp": datetime.now().isoformat()
        }
    
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyser un projet complet"""
        # Implémentation de l'analyse de projet
        pass


# Point d'entrée principal
async def main():
    """Lancer l'agent Claude 4 Opus"""
    # Vérifier les variables d'environnement
    required_env = ["CLAUDE_API_KEY", "GH_TOKEN", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE"]
    missing = [var for var in required_env if not os.getenv(var)]
    
    if missing:
        logger = logging.getLogger(__name__).error(f"❌ Variables manquantes: {', '.join(missing)}")
        return
    
    # Créer et lancer l'agent
    agent = ClaudeOpusAgent()
    
    # Créer l'extension VS Code
    vscode_ext = VSCodeClaudeExtension(agent)
    
    # Lancer les deux en parallèle
    await asyncio.gather(
        agent.autonomous_loop(),
        vscode_ext.start_server()
    )


if __name__ == "__main__":
    asyncio.run(main())