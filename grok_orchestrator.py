#!/usr/bin/env python3
"""
GROK Orchestrator - Manages the autonomous operations of GROK AI system.

This module handles core system operations including:
- Repository and resource management
- AI workflows and autonomous decision processes
- Monitoring and event triggers
- System self-improvement routines
"""

import json
import logging
import os
import random
import subprocess
import time
from typing import Any, Dict, List, Optional

import requests
from github import Github

from supabase import create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Mock classes to allow code to work without langgraph
class MockState:
    def __init__(self):
        self.log_entry = {}


class MockStateGraph:
    def __init__(self, *args, **kwargs):
        pass

    def add_node(self, *args, **kwargs):
        pass

    def add_edge(self, *args, **kwargs):
        pass

    def add_conditional_edges(self, *args, **kwargs):
        pass

    def set_entry_point(self, *args, **kwargs):
        pass

    def compile(self, *args, **kwargs):
        return self

    def invoke(self, state):
        return state


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
        logger.warning(
            "Using custom State class as langgraph.prelude could not be imported"
        )

    LANGGRAPH_AVAILABLE = True
    logger.info("LangGraph package successfully imported.")
except ImportError:
    logger.warning("LangGraph package not found. Some features will be disabled.")


# Environment variables and constants with proper error handling
def get_required_env(var_name: str) -> str:
    """Get required environment variable or raise ValueError."""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} environment variable is required but not set")
    return value


def get_optional_env(var_name: str, default: str = "") -> str:
    """Get optional environment variable with default."""
    return os.getenv(var_name, default)


# Load environment variables with proper error handling
try:
    XAI_API_KEY = get_optional_env("XAI_API_KEY")
    GH_TOKEN = get_optional_env("GH_TOKEN")
    GH_REPO_DEV = get_optional_env("GH_REPO_DEV", "yannabadie/appia-dev")
    GH_REPO_AI = get_optional_env("GH_REPO_AI", "yannabadie/appIA")
    SUPABASE_URL = get_optional_env("SUPABASE_URL")
    SUPABASE_KEY = get_optional_env("SUPABASE_KEY")
    SUPABASE_PROJECT_ID = get_optional_env("SUPABASE_PROJECT_ID")
    SUPABASE_SERVICE_ROLE = get_optional_env("SUPABASE_SERVICE_ROLE")
    SUPABASE_ACCESS_TOKEN = get_optional_env("SUPABASE_ACCESS_TOKEN")
    OPENAI_API_KEY = get_optional_env("OPENAI_API_KEY")
    GEMINI_API_KEY = get_optional_env("GEMINI_API_KEY")
    SECRET_ACCESS_TOKEN = get_optional_env("SECRET_ACCESS_TOKEN")

    # Handle GCP credentials
    gcp_sa_json_str = get_optional_env("GCP_SA_JSON")
    GCP_SA_JSON = json.loads(gcp_sa_json_str) if gcp_sa_json_str else {}

except Exception as e:
    logger.warning(f"Environment variable setup warning: {e}")
    # Set safe defaults
    XAI_API_KEY = ""
    GH_TOKEN = ""
    GH_REPO_DEV = "yannabadie/appia-dev"
    GH_REPO_AI = "yannabadie/appIA"
    SUPABASE_URL = ""
    SUPABASE_KEY = ""
    SUPABASE_PROJECT_ID = ""
    SUPABASE_SERVICE_ROLE = ""
    SUPABASE_ACCESS_TOKEN = ""
    OPENAI_API_KEY = ""
    GEMINI_API_KEY = ""
    SECRET_ACCESS_TOKEN = ""
    GCP_SA_JSON = {}

# Initialize clients with error handling
github = None
repo_dev = None
repo_ai = None
supabase = None
gcp_credentials = None

try:
    if GH_TOKEN:
        github = Github(GH_TOKEN)
        repo_dev = github.get_repo(GH_REPO_DEV)
        repo_ai = github.get_repo(GH_REPO_AI)
except Exception as e:
    logger.warning(f"GitHub client initialization failed: {e}")

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.warning(f"Supabase client initialization failed: {e}")

try:
    if GCP_SA_JSON:
        from google.oauth2 import service_account

        gcp_credentials = service_account.Credentials.from_service_account_info(
            GCP_SA_JSON
        )
except Exception as e:
    logger.warning(f"GCP credentials initialization failed: {e}")

# Global state for tracking operations
state = MockState()

# Repository directories
REPO_DIR_DEV = "appia-dev"
REPO_DIR_AI = "appIA"


# Repository clone/sync functions
def ensure_repository(dir_path: str, repo_url: str, token: str) -> bool:
    """Ensure repository is cloned and up to date."""
    try:
        if not os.path.exists(dir_path):
            if token:
                cmd = f"git clone https://x-access-token:{token}@github.com/{repo_url}.git {dir_path}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.returncode == 0
        else:
            original_dir = os.getcwd()
            os.chdir(dir_path)
            result = subprocess.run(
                "git pull origin grok-evolution",
                shell=True,
                capture_output=True,
                text=True,
            )
            os.chdir(original_dir)
            return result.returncode == 0
    except Exception as e:
        logger.error(f"Repository synchronization error: {e}")
        return False


# Initialize repositories if tokens are available
if GH_TOKEN:
    ensure_repository(REPO_DIR_DEV, GH_REPO_DEV, GH_TOKEN)
    ensure_repository(REPO_DIR_AI, GH_REPO_AI, GH_TOKEN)


# État
class AgentState(State):
    """Agent state for tracking workflow progress."""

    def __init__(self):
        super().__init__()
        self.task = ""
        self.sub_agent = ""
        self.repo_dir = ""
        self.repo_obj = None
        self.code_generated = ""
        self.test_result = ""
        self.reflection = ""
        self.doc_update = ""
        self.log_entry = {}
        self.lint_fixed = False


# Query Grok (créativité temp=0.5, fallback multi-LLMs pour adaptabilité)
def query_grok(prompt: str) -> str:
    """Query Grok API with fallbacks to other LLMs."""
    full_prompt = f"Contexte JARVYS_DEV (cloud, MCP/GCP, mémoire Supabase, génère JARVYS_AI in appIA) et JARVYS_AI (local, routing LLMs, self-improve): {prompt}. Sois créatif (innovations alignées comme sentiment analysis ou quantum sim), proactif (suggère extras), adaptable (handle unknown via alternatives)."

    # Try Grok first
    if XAI_API_KEY:
        try:
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {XAI_API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "grok-4",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.5,
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            state.log_entry["grok_error"] = str(e)

    # Fallback to Gemini
    if GEMINI_API_KEY:
        try:
            url_f = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            data_f = {"contents": [{"parts": [{"text": full_prompt}]}]}
            response = requests.post(url_f, json=data_f, timeout=30)
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            state.log_entry["gemini_error"] = str(e)

    # Ultimate fallback to OpenAI
    if OPENAI_API_KEY:
        try:
            url_o = "https://api.openai.com/v1/chat/completions"
            headers_o = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            data_o = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": full_prompt}],
            }
            response = requests.post(url_o, headers=headers_o, json=data_o, timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            state.log_entry["openai_error"] = str(e)

    # Return default response if all APIs fail
    return f"Unable to query AI APIs. Task: {prompt[:100]}..."


# Node: Fix Lint/Erreurs (proactif/adaptable : auto-fix, query si unknown)
def fix_lint(agent_state: AgentState) -> AgentState:
    """Fix linting issues in the repository."""
    if not agent_state.repo_dir:
        agent_state.repo_dir = REPO_DIR_DEV

    original_dir = os.getcwd()

    try:
        os.chdir(agent_state.repo_dir)
        agent_state.log_entry["lint_output"] = ""

        commands = [
            "poetry run ruff check --fix --unsafe-fixes . || echo 'Ruff failed'",
            "poetry run black . || echo 'Black failed'",
            (
                "pre-commit run --all-files || echo 'Pre-commit failed'"
                if os.path.exists(".pre-commit-config.yaml")
                else "echo 'No pre-commit'"
            ),
            "poetry install --with dev || echo 'Poetry install failed'",
        ]

        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=300
                )
                output = result.stdout + result.stderr
                agent_state.log_entry["lint_output"] += output[:200] + "\n"
            except subprocess.TimeoutExpired:
                agent_state.log_entry["lint_output"] += f"Timeout for command: {cmd}\n"
            except Exception as e:
                # Adaptabilité : Query pour solution inconnue
                prompt = f"Erreur in Codespace: {str(e)}. Génère fix commande pour Ruff/Black/Poetry lint bugs (E501/F841 etc.). Sois proactif/créatif (alt tools si fail)."
                fix_cmd = query_grok(prompt)
                try:
                    subprocess.run(fix_cmd, shell=True, timeout=60)
                    agent_state.log_entry["adapt_fix"] = fix_cmd
                except:
                    agent_state.log_entry["adapt_fix_failed"] = fix_cmd

        # Vérification
        try:
            check_result = subprocess.run(
                "ruff check . || echo 'No ruff'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            check = check_result.stdout
            agent_state.lint_fixed = (
                "no issues" in check.lower() or "All checks passed" in check
            )
        except:
            agent_state.lint_fixed = False

        # Log Supabase (avec SERVICE_ROLE pour auth avancé si besoin)
        if supabase and SUPABASE_SERVICE_ROLE:
            try:
                supabase.auth.sign_in_with_password(
                    {"email": "service@example.com", "password": SUPABASE_SERVICE_ROLE}
                )
                supabase.table("logs").insert(agent_state.log_entry).execute()
            except Exception as e:
                logger.warning(f"Supabase logging failed: {e}")

    finally:
        os.chdir(original_dir)

    return agent_state


# Node: Identifier Tâches (proactif : base + créatives aléatoires)
def identify_tasks(agent_state: AgentState) -> AgentState:
    """Identify tasks to work on."""
    is_ai = random.choice([True, False])
    agent_state.repo_dir = REPO_DIR_AI if is_ai else REPO_DIR_DEV
    agent_state.repo_obj = repo_ai if is_ai else repo_dev
    agent_state.sub_agent = "AI" if is_ai else "DEV"

    original_dir = os.getcwd()

    try:
        os.chdir(agent_state.repo_dir)

        issues = []
        if agent_state.repo_obj:
            try:
                issues = [
                    i.title for i in agent_state.repo_obj.get_issues(state="open")
                ]
            except Exception as e:
                logger.warning(f"Failed to get GitHub issues: {e}")

        # Test output
        try:
            test_result = subprocess.run(
                "pytest -q || echo 'No pytest'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            test_output = test_result.stdout
            failing = [line for line in test_output.splitlines() if "FAILED" in line]
        except:
            failing = []

        base_tasks = (
            issues
            + failing
            + ["Optim coûts >$3", "Ajouter pruning mémoire", "Impl Docker hybrid"]
        )
        creative_tasks = [
            "Ajouter sentiment analysis user (créatif: moods predict)",
            "Intégrer quantum sim routing (créatif: qubits decisions)",
            "Proactif: Auto-fine-tune LLM sur feedback",
        ]

        tasks = base_tasks + random.sample(
            creative_tasks, random.randint(1, min(2, len(creative_tasks)))
        )

        if agent_state.sub_agent == "DEV":
            tasks += ["Générer/update JARVYS_AI et push to appIA"]

        agent_state.task = (
            random.choice(tasks)
            if tasks
            else "Proactif: Propose new feature architecture"
        )

        agent_state.log_entry = {
            "task": agent_state.task,
            "repo": agent_state.sub_agent,
            "status": "identified",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if supabase:
            try:
                supabase.table("logs").insert(agent_state.log_entry).execute()
            except Exception as e:
                logger.warning(f"Supabase logging failed: {e}")

    finally:
        os.chdir(original_dir)

    return agent_state


# Node: Générer Code
def generate_code(agent_state: AgentState) -> AgentState:
    """Generate code for the identified task."""
    prompt = f"Génère code/fix pour '{agent_state.task}' sur {agent_state.sub_agent}. Utilise env/secrets (e.g., SUPABASE_SERVICE_ROLE auth, GCP_SA_JSON cloud). Si générer JARVYS_AI, output pour push appIA."
    agent_state.code_generated = query_grok(prompt)

    if "générer JARVYS_AI" in agent_state.task.lower():
        original_dir = os.getcwd()
        try:
            os.chdir(REPO_DIR_AI)
            file_path = (
                f"src/jarvys_ai/generated_{agent_state.task.replace(' ', '_')}.py"
            )
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(agent_state.code_generated)

            if GH_TOKEN:
                try:
                    subprocess.run(
                        f"git add . && git commit -m 'Generated by JARVYS_DEV: {agent_state.task}' && git push origin main",
                        shell=True,
                        timeout=60,
                    )
                except Exception as e:
                    logger.warning(f"Git operations failed: {e}")
        finally:
            os.chdir(original_dir)

    return agent_state


# Node: Appliquer & Tester
def apply_test(agent_state: AgentState) -> AgentState:
    """Apply generated code and test it."""
    original_dir = os.getcwd()

    try:
        os.chdir(agent_state.repo_dir)

        file_path = f"src/jarvys_{agent_state.sub_agent.lower()}/updated_{agent_state.task.replace(' ', '_')}.py"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(agent_state.code_generated)

        # Re-fix lint post-génération
        try:
            subprocess.run(
                f"ruff check --fix {file_path} || echo 'Ruff fix failed'",
                shell=True,
                timeout=60,
            )
        except:
            pass

        # Test the file
        try:
            test_result = subprocess.run(
                f"pytest {file_path} || echo 'Pytest failed'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            agent_state.test_result = test_result.stdout + test_result.stderr
        except:
            agent_state.test_result = "Test execution failed"

        agent_state.log_entry["test_result"] = agent_state.test_result[:500]

        if supabase:
            try:
                supabase.table("logs").update(agent_state.log_entry).eq(
                    "task", agent_state.task
                ).execute()
            except Exception as e:
                logger.warning(f"Supabase update failed: {e}")

    finally:
        os.chdir(original_dir)

    return agent_state


# Node: Update Docs
def update_docs(agent_state: AgentState) -> AgentState:
    """Update documentation."""
    prompt = f"Génère update doc Markdown pour '{agent_state.task}' sur {agent_state.sub_agent}. Sections: Description, Changements, Impact, Exemples. Créatif: Ajoute analogies/ideas fun alignées."
    agent_state.doc_update = query_grok(prompt)

    original_dir = os.getcwd()

    try:
        os.chdir(agent_state.repo_dir)

        with open("README.md", "a", encoding="utf-8") as f:
            f.write(
                f"\n## Update: {agent_state.task} ({time.strftime('%Y-%m-%d')})\n{agent_state.doc_update}\n"
            )

        try:
            subprocess.run("git add README.md", shell=True, timeout=30)
        except:
            pass

        agent_state.log_entry["doc_update"] = agent_state.doc_update[:500]

        if supabase:
            try:
                supabase.table("logs").update(agent_state.log_entry).eq(
                    "task", agent_state.task
                ).execute()
            except Exception as e:
                logger.warning(f"Supabase update failed: {e}")

    finally:
        os.chdir(original_dir)

    return agent_state


# Node: Self-Reflect & Commit/PR
def reflect_commit(agent_state: AgentState) -> AgentState:
    """Reflect on results and commit/create PR."""
    if "FAILED" in agent_state.test_result:
        prompt = f"Reflect: Failed '{agent_state.test_result}'. Improve, créatif/proactif (alt approaches), adaptable (handle unknown)."
        agent_state.reflection = query_grok(prompt)
        agent_state.log_entry["reflection"] = agent_state.reflection

        if supabase:
            try:
                supabase.table("logs").update(agent_state.log_entry).eq(
                    "task", agent_state.task
                ).execute()
            except Exception as e:
                logger.warning(f"Supabase update failed: {e}")

        return agent_state  # Will trigger retry logic in graph
    else:
        original_dir = os.getcwd()

        try:
            os.chdir(agent_state.repo_dir)

            if GH_TOKEN:
                try:
                    subprocess.run(
                        f"git add . && git commit -m 'Grok Auto: {agent_state.task} with docs' && git push origin grok-evolution",
                        shell=True,
                        timeout=120,
                    )

                    if agent_state.repo_obj:
                        pr = agent_state.repo_obj.create_pull(
                            title=f"Grok PR: {agent_state.task}",
                            body=f"Code: {agent_state.code_generated[:500]}\nDocs: {agent_state.doc_update[:500]}\nLog: {str(agent_state.log_entry)}",
                            head="grok-evolution",
                            base="main",
                        )
                        agent_state.log_entry["pr_url"] = pr.html_url

                        # Transparence: Créer issue avec full log
                        agent_state.repo_obj.create_issue(
                            title=f"Grok Log: {agent_state.task} Completed",
                            body=str(agent_state.log_entry),
                        )
                except Exception as e:
                    logger.warning(f"Git/GitHub operations failed: {e}")
                    agent_state.log_entry["git_error"] = str(e)

            agent_state.log_entry["status"] = "completed"

            if supabase:
                try:
                    supabase.table("logs").update(agent_state.log_entry).eq(
                        "task", agent_state.task
                    ).execute()
                except Exception as e:
                    logger.warning(f"Supabase update failed: {e}")

        finally:
            os.chdir(original_dir)

    return agent_state


# Build Graph
def build_orchestrator_graph():
    """Build the orchestrator graph with proper error handling."""
    try:
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

        # Conditional edges with proper handling
        def should_retry_from_reflect(agent_state: AgentState) -> str:
            """Determine if we should retry from generate or end."""
            return "generate" if "FAILED" in agent_state.test_result else END

        def should_retry_lint(agent_state: AgentState) -> str:
            """Determine if we should retry lint or continue."""
            return "fix_lint" if not agent_state.lint_fixed else "identify"

        graph.add_conditional_edges(
            "reflect_commit",
            should_retry_from_reflect,
            {"generate": "generate", END: END},
        )
        graph.add_conditional_edges(
            "fix_lint",
            should_retry_lint,
            {"fix_lint": "fix_lint", "identify": "identify"},
        )

        return graph.compile()
    except Exception as e:
        logger.error(f"Failed to build graph: {e}")
        return None


# Initialize orchestrator
orchestrator = build_orchestrator_graph()


def run_orchestrator():
    """Run the orchestrator with proper error handling."""
    if not orchestrator:
        logger.error("Orchestrator not initialized. Exiting.")
        return

    logger.info("Starting GROK Orchestrator...")

    max_cycles = 10  # Guard global
    cycle = 0

    while cycle < max_cycles:
        try:
            logger.info(f"Starting cycle {cycle + 1}/{max_cycles}")

            # Create new state for each cycle
            agent_state = AgentState()

            # Run the orchestrator
            final_state = orchestrator.invoke(agent_state)

            logger.info(
                f"Cycle {cycle + 1} completed. Task: {final_state.get('task', 'Unknown')}"
            )

            # Sleep for 1 hour between cycles
            logger.info("Sleeping for 1 hour...")
            time.sleep(3600)

            cycle += 1

        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error in orchestrator cycle {cycle + 1}: {e}")
            cycle += 1
            # Sleep for 5 minutes on error before retrying
            time.sleep(300)

    logger.info("GROK Orchestrator finished.")


if __name__ == "__main__":
    run_orchestrator()
