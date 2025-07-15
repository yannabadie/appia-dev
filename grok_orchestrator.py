#!/usr/bin/env python3
"""
Grok Orchestrator: Intelligent workflow automation system for appia-dev/appIA repositories.

This script provides an advanced workflow automation system for managing development tasks,
repository synchronization, and AI-driven code improvements across multiple repositories.
The orchestrator handles GitHub integration, continuous testing, and coordinates
with Supabase for state management.

Environment Variables:
    GH_TOKEN: GitHub Personal Access Token
    SUPABASE_URL: URL for Supabase instance
    SUPABASE_KEY: Supabase API key
    OPENAI_API_KEY: OpenAI API key for AI-powered assistance
    GEMINI_API_KEY: Google Gemini API key for additional AI models
"""

import os
import time
import subprocess
import logging
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables and constants
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE = os.environ.get("SUPABASE_SERVICE_ROLE", "")

# Global state for tracking operations
state = MockState()

import requests
from github import Github
from supabase import create_client

# Mock classes to allow code to work without langgraph
class MockState:
    def __init__(self):
        self.log_entry = {}

# Define mock classes first for graceful fallbacks
class MockStateGraph:
    def __init__(self, *args, **kwargs):
        pass
    def add_node(self, *args, **kwargs):
        pass
    def add_edge(self, *args, **kwargs):
        pass
    def compile(self, *args, **kwargs):
        return self

# Base State class for our state system
class State(dict):
    """Base State class (mock for LangGraph State)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __setattr__(self, key, value):
        self[key] = value
        
    def __getattr__(self, key):
        return self.get(key)

# Set defaults assuming imports will fail
StateGraph = MockStateGraph
END = "END"
LANGGRAPH_AVAILABLE = False

# Now attempt to import LangGraph
try:
    import langgraph.graph
    # If we get here, imports succeeded
    StateGraph = langgraph.graph.StateGraph
    END = langgraph.graph.END
    
    # Try to import State from langgraph.prelude with error suppression
    try:
        # pylint: disable=all
        # flake8: noqa
        # type: ignore
        from langgraph.prelude import State as LangGraphState  # type: ignore
        # pylint: enable=all
        State = LangGraphState
    except (ImportError, ModuleNotFoundError):
        # Keep our custom State class
        logger.warning("Using custom State class as langgraph.prelude could not be imported")
        
    LANGGRAPH_AVAILABLE = True
    logger.info("LangGraph package successfully imported.")
except ImportError:
    logger.warning("LangGraph package not found. Some features will be disabled.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("grok_orchestrator")

# Load environment variables with proper error handling
def get_env(key: str, required: bool = True, default: Any = None) -> Any:
    """Get environment variable with proper error handling."""
    value = os.getenv(key)
    if value is None and required:
        raise EnvironmentError(f"Required environment variable '{key}' is missing")
    return value if value is not None else default

# Environment configuration
GH_TOKEN = get_env('GH_TOKEN')
GH_REPO_DEV = get_env('GH_REPO_DEV', False, 'yannabadie/appia-dev')
GH_REPO_AI = get_env('GH_REPO_AI', False, 'yannabadie/appIA')
SUPABASE_URL = get_env('SUPABASE_URL')
SUPABASE_KEY = get_env('SUPABASE_KEY')
OPENAI_API_KEY = get_env('OPENAI_API_KEY', False)
GEMINI_API_KEY = get_env('GEMINI_API_KEY', False)

# Initialize clients
try:
    logger.info("Initializing GitHub client")
    github = Github(GH_TOKEN)
    repo_dev = github.get_repo(GH_REPO_DEV)
    repo_ai = github.get_repo(GH_REPO_AI)
    
    logger.info("Initializing Supabase client")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.error(f"Failed to initialize clients: {e}")
    raise

# Repository synchronization
REPO_DIR_DEV = 'appia-dev'
REPO_DIR_AI = 'appIA'

def sync_repository(dir_path: str, repo_url: str, branch: str = "main") -> bool:
    """
    Synchronize a local repository with its remote counterpart.
    
    Args:
        dir_path: Local directory path for the repository
        repo_url: GitHub repository URL in format 'owner/repo'
        branch: Branch to sync (default: main)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not Path(dir_path).exists():
            logger.info(f"Cloning repository {repo_url} to {dir_path}")
            result = subprocess.run(
                f"git clone https://x-access-token:{GH_TOKEN}@github.com/{repo_url}.git {dir_path}",
                shell=True, check=True, capture_output=True, text=True
            )
        else:
            cwd = os.getcwd()
            try:
                os.chdir(dir_path)
                logger.info(f"Pulling latest changes from {branch} branch in {repo_url}")
                result = subprocess.run(
                    f"git pull origin {branch}",
                    shell=True, check=True, capture_output=True, text=True
                )
            finally:
                os.chdir(cwd)
                
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Repository synchronization error: {e}")
        return False

# État
class AgentState(State):
    task: str
    sub_agent: str
    repo_dir: str
    repo_obj: object
    code_generated: str
    test_result: str
    reflection: str
    doc_update: str
    log_entry: dict
    lint_fixed: bool = False

# Query Grok (créativité temp=0.5, fallback multi-LLMs pour adaptabilité)
def query_grok(prompt: str) -> str:
    full_prompt = f"Contexte JARVYS_DEV (cloud, MCP/GCP, mémoire Supabase, génère JARVYS_AI in appIA) et JARVYS_AI (local, routing LLMs, self-improve): {prompt}. Sois créatif (innovations alignées comme sentiment analysis ou quantum sim), proactif (suggère extras), adaptable (handle unknown via alternatives)."
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "grok-4", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.5}
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        state.log_entry['error'] = str(e)
        # Fallback proactif Gemini
        try:
            url_f = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            data_f = {"contents": [{"parts": [{"text": full_prompt}]}]}
            response = requests.post(url_f, json=data_f)
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            # Ultime fallback OpenAI
            url_o = "https://api.openai.com/v1/chat/completions"
            headers_o = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            data_o = {"model": "gpt-4", "messages": [{"role": "user", "content": full_prompt}]}
            response = requests.post(url_o, headers=headers_o, json=data_o)
            return response.json()['choices'][0]['message']['content']

# Node: Fix Lint/Erreurs (proactif/adaptable : auto-fix, query si unknown)
def fix_lint(state: AgentState) -> AgentState:
    os.chdir(state.repo_dir)
    commands = [
        "poetry run ruff check --fix --unsafe-fixes .",
        "poetry run black .",
        "pre-commit run --all-files" if os.path.exists('.pre-commit-config.yaml') else "echo 'No pre-commit'",
        "poetry install --with dev"  # Fix Poetry env issues
    ]
    for cmd in commands:
        try:
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
            state.log_entry['lint_output'] += output[:200] + '\n'
        except Exception as e:
            # Adaptabilité : Query pour solution inconnue
            prompt = f"Erreur in Codespace: {str(e)}. Génère fix commande pour Ruff/Black/Poetry lint bugs (E501/F841 etc.). Sois proactif/créatif (alt tools si fail)."
            fix_cmd = query_grok(prompt)
            subprocess.run(fix_cmd, shell=True)
            state.log_entry['adapt_fix'] = fix_cmd
    
    # Vérif
    check = subprocess.run("ruff check .", shell=True, capture_output=True, text=True).stdout
    state.lint_fixed = "no issues" in check.lower()
    
    # Log Supabase (avec SERVICE_ROLE pour auth avancé si besoin)
    if SUPABASE_SERVICE_ROLE:
        supabase.auth.sign_in_with_password({'email': 'service@example.com', 'password': SUPABASE_SERVICE_ROLE})
    supabase.table('logs').insert(state.log_entry).execute()
    
    return state

# Node: Identifier Tâches (proactif : base + créatives aléatoires)
def identify_tasks(state: AgentState) -> AgentState:
    is_ai = random.choice([True, False])
    state.repo_dir = REPO_DIR_AI if is_ai else REPO_DIR_DEV
    state.repo_obj = repo_ai if is_ai else repo_dev
    state.sub_agent = "AI" if is_ai else "DEV"
    
    os.chdir(state.repo_dir)
    
    issues = [i.title for i in state.repo_obj.get_issues(state="open")]
    test_output = subprocess.run("pytest -q", shell=True, capture_output=True, text=True).stdout
    failing = [line for line in test_output.splitlines() if "FAILED" in line]
    base_tasks = issues + failing + ["Optim coûts >$3", "Ajouter pruning mémoire", "Impl Docker hybrid"]
    creative_tasks = ["Ajouter sentiment analysis user (créatif: moods predict)", "Intégrer quantum sim routing (créatif: qubits decisions)", "Proactif: Auto-fine-tune LLM sur feedback"]
    tasks = base_tasks + random.sample(creative_tasks, random.randint(1, 2))  # Proactif: 1-2 créatives
    if state.sub_agent == "DEV":
        tasks += ["Générer/update JARVYS_AI et push to appIA"]
    state.task = random.choice(tasks) if tasks else "Proactif: Propose new feature architecture"
    
    state.log_entry = {'task': state.task, 'repo': state.sub_agent, 'status': 'identified', 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")}
    supabase.table('logs').insert(state.log_entry).execute()
    
    return state

# Node: Générer Code
def generate_code(state: AgentState) -> AgentState:
    prompt = f"Génère code/fix pour '{state.task}' sur {state.sub_agent}. Utilise env/secrets (e.g., SUPABASE_SERVICE_ROLE auth, GCP_SA_JSON cloud). Si générer JARVYS_AI, output pour push appIA."
    state.code_generated = query_grok(prompt)
    
    if "générer JARVYS_AI" in state.task.lower():
        os.chdir(REPO_DIR_AI)
        file_path = f"src/jarvys_ai/generated_{state.task.replace(' ', '_')}.py"
        with open(file_path, 'w') as f:
            f.write(state.code_generated)
        os.system(f"git add . && git commit -m 'Generated by JARVYS_DEV: {state.task}' && git push origin main")  # Assume main pour AI
        os.chdir(state.repo_dir)
    
    return state

# Node: Appliquer & Tester
def apply_test(state: AgentState) -> AgentState:
    file_path = f"src/jarvys_{state.sub_agent.lower()}/updated_{state.task.replace(' ', '_')}.py"
    with open(file_path, 'w') as f:
        f.write(state.code_generated)
    
    # Re-fix lint post-génération
    subprocess.run(f"ruff check --fix {file_path}", shell=True)
    
    state.test_result = subprocess.run(f"pytest {file_path}", shell=True, capture_output=True, text=True).stdout
    state.log_entry['test_result'] = state.test_result[:500]
    supabase.table('logs').update(state.log_entry).eq('task', state.task).execute()
    
    return state

# Node: Update Docs
def update_docs(state: AgentState) -> AgentState:
    prompt = f"Génère update doc Markdown pour '{state.task}' sur {state.sub_agent}. Sections: Description, Changements, Impact, Exemples. Créatif: Ajoute analogies/ideas fun alignées."
    state.doc_update = query_grok(prompt)
    
    with open('README.md', 'a') as f:
        f.write(f"\n## Update: {state.task} ({time.strftime('%Y-%m-%d')})\n{state.doc_update}\n")
    
    os.system("git add README.md")
    state.log_entry['doc_update'] = state.doc_update[:500]
    supabase.table('logs').update(state.log_entry).eq('task', state.task).execute()
    
    return state

# Node: Self-Reflect & Commit/PR
def reflect_commit(state: AgentState) -> AgentState:
    if "FAILED" in state.test_result:
        prompt = f"Reflect: Failed '{state.test_result}'. Improve, créatif/proactif (alt approaches), adaptable (handle unknown)."
        state.reflection = query_grok(prompt)
        state.log_entry['reflection'] = state.reflection
        supabase.table('logs').update(state.log_entry).eq('task', state.task).execute()
        return {"next": "generate_code"}
    else:
        os.system(f"git add . && git commit -m 'Grok Auto: {state.task} with docs' && git push origin grok-evolution")
        pr = state.repo_obj.create_pull(title=f"Grok PR: {state.task}", body=f"Code: {state.code_generated}\nDocs: {state.doc_update}\nLog: {str(state.log_entry)}", head="grok-evolution", base="main")
        state.log_entry['pr_url'] = pr.html_url
        
        # Transparence: Créer issue avec full log
        state.repo_obj.create_issue(title=f"Grok Log: {state.task} Completed", body=str(state.log_entry))
        
        state.log_entry['status'] = 'completed'
        supabase.table('logs').update(state.log_entry).eq('task', state.task).execute()
    
    return state

# Build Graph
graph = StateGraph(AgentState)
graph.add_node("fix_lint", fix_lint)
graph.add_node("identify", identify_tasks)
graph.add_node("generate", generate_code)
graph.add_node("apply_test", apply_test)
graph.add_node("update_docs", update_docs)
graph.add_node("reflect_commit", reflect_commit)

graph.set_entry_point("fix_lint")
graph.add_edge("fix_lint", "identify")
graph.add_edge("identify", "generate")
graph.add_edge("generate", "apply_test")
graph.add_edge("apply_test", "update_docs")
graph.add_edge("update_docs", "reflect_commit")
graph.add_conditional_edges("reflect_commit", lambda s: "generate" if "FAILED" in s.test_result else END, {"generate": "generate", END: END})
graph.add_conditional_edges("fix_lint", lambda s: "fix_lint" if not s.lint_fixed else "identify", {"fix_lint": "fix_lint", "identify": "identify"})

orchestrator = graph.compile()

def run_orchestrator():
    state = AgentState(task="", sub_agent="", repo_dir="", repo_obj=None, code_generated="", test_result="", reflection="", doc_update="", log_entry={}, lint_fixed=False)
    max_cycles = 10  # Guard global
    cycle = 0
    while cycle < max_cycles:
        state = orchestrator.invoke(state)
        time.sleep(3600)  # 1h
        cycle += 1

if __name__ == "__main__":
    run_orchestrator()