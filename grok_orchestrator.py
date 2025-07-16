import sys
import json
import operator  # For reducers
import os
import random
import subprocess
import time

import requests
from github import Github
from google.oauth2 import service_account
from langgraph.graph import END, StateGraph
from typing_extensions import Annotated, TypedDict

from supabase import create_client

# Load TOUS secrets (périmètre complet, raise si manquant critique)
XAI_API_KEY = os.getenv("XAI_API_KEY") or ValueError("XAI_API_KEY manquant")
GH_TOKEN = os.getenv("GH_TOKEN") or ValueError("GH_TOKEN manquant")
GH_REPO_DEV = os.getenv("GH_REPO_DEV", "yannabadie/appia-dev")
GH_REPO_AI = os.getenv("GH_REPO_AI", "yannabadie/appIA")
SUPABASE_URL = os.getenv("SUPABASE_URL") or ValueError("SUPABASE_URL manquant")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ValueError("SUPABASE_KEY manquant")
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GCP_SA_JSON = (
    json.loads(os.getenv("GCP_SA_JSON"))
    if os.getenv("GCP_SA_JSON")
    else ValueError("GCP_SA_JSON manquant")
)
SECRET_ACCESS_TOKEN = os.getenv("SECRET_ACCESS_TOKEN")  # Loadé même inusité

# GCP Credentials (pour tâches cloud/adaptabilité)
gcp_credentials = service_account.Credentials.from_service_account_info(GCP_SA_JSON)

# Clients (use SUPABASE_SERVICE_ROLE as key for elevated client = None if needed)
supabase_client_key = SUPABASE_SERVICE_ROLE if SUPABASE_SERVICE_ROLE else SUPABASE_KEY
supabase = create_client(SUPABASE_URL, supabase_client_key)

# GitHub clients
github = Github(GH_TOKEN)
repo_dev = github.get_repo(GH_REPO_DEV)
repo_ai = github.get_repo(GH_REPO_AI)

# Dirs repos (clone/pull pour synchro)
REPO_DIR_DEV = "appia-dev"
REPO_DIR_AI = "appIA"
for dir_path, repo_url, branch in [
    (REPO_DIR_DEV, GH_REPO_DEV, "grok-evolution"),
    (REPO_DIR_AI, GH_REPO_AI, "main"),
]:
    if not os.path.exists(dir_path):
        os.system(
            f"git clone https://x-access-token:{GH_TOKEN}@github.com/{repo_url}.git {dir_path}"
        )
    else:
        os.chdir(dir_path)
        # Checkout the correct branch for each repo
        subprocess.run(["git", "checkout", branch], check=True)
        subprocess.run(["git", "pull", "origin", branch], check=True)
        os.chdir("..")

        # Check if branch exists remotely
        branch_check = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", "grok-evolution"],
            capture_output=True,
            text=True,
        )
        if "grok-evolution" not in branch_check.stdout:
            subprocess.run(["git", "checkout", "-b", "grok-evolution"], check=True)
            subprocess.run(
                ["git", "push", "-u", "origin", "grok-evolution"], check=True
            )
        else:
            try:
                subprocess.check_call(["git", "checkout", "grok-evolution"])
            except subprocess.CalledProcessError:
                subprocess.run(
                    [
                        "git",
                        "checkout",
                        "-b",
                        "grok-evolution",
                        "origin/grok-evolution",
                    ],
                    check=True,
                )
        subprocess.run(["git", "pull", "origin", "grok-evolution"], check=True)


# État (TypedDict avec reducers pour éviter InvalidUpdateError)
class AgentState(TypedDict):
    task: str
    sub_agent: str
    repo_dir: str
    repo_obj: object
    code_generated: str
    test_result: str
    reflection: str
    doc_update: str
    log_entry: Annotated[
        dict, operator.setitem
    ]  # Reducer for dict updates (overrides keys)
    lint_fixed: bool


# Query Grok (créativité temp=0.5, fallback multi-LLMs pour adaptabilité)
def query_grok(prompt: str, state: AgentState) -> str:  # Pass state for log
    full_prompt = f"Contexte JARVYS_DEV (cloud, MCP/GCP, mémoire Supabase, génère JARVYS_AI in appIA) et JARVYS_AI (local, routing LLMs, self-improve): {prompt}. Sois créatif (innovations alignées comme sentiment analysis ou quantum sim), proactif (suggère extras), adaptable (handle unknown via alternatives)."
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
        response = requests.post(url, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        state["log_entry"] = {**state["log_entry"], "error": str(e)}
        # Fallback proactif Gemini
        try:
            url_f = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            data_f = {"contents": [{"parts": [{"text": full_prompt}]}]}
            response = requests.post(url_f, json=data_f)
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            # Ultime fallback OpenAI
            url_o = "https://api.openai.com/v1/chat/completions"
            headers_o = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            data_o = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": full_prompt}],
            }
            response = requests.post(url_o, headers=headers_o, json=data_o)
            return response.json()["choices"][0]["message"]["content"]


# Node: Fix Lint/Erreurs (proactif/adaptable : auto-fix, query si unknown)
def fix_lint(state: AgentState) -> AgentState:
    os.chdir(state["repo_dir"])
    commands = [
        "poetry run ruff check --fix --unsafe-fixes .",
        "poetry run black .",
        (
            "pre-commit run --all-files"
            if os.path.exists(".pre-commit-config = {}.yaml")
            else "echo 'No pre-commit'"
        ),
        "poetry install --with dev",  # Fix Poetry env issues
    ]
    for cmd in commands:
        try:
            output = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            ).stdout
            state["log_entry"] = {
                **state["log_entry"],
                "lint_output": state["log_entry"].get("lint_output", "")
                + output[:200]
                + "\n",
            }
        except Exception as e:
            # Adaptabilité : Query pour solution inconnue
            prompt = f"Erreur in Codespace: {str(e)}. Génère fix commande pour Ruff/Black/Poetry lint bugs (E501/F841 etc.). Sois proactif/créatif (alt tools si fail)."
            fix_cmd = query_grok(prompt, state)
            subprocess.run(fix_cmd, shell=True)
            state["log_entry"] = {**state["log_entry"], "adapt_fix": fix_cmd}

    # Vérif
    check = subprocess.run(
        "ruff check .", shell=True, capture_output=True, text=True
    ).stdout
    state["lint_fixed"] = "no issues" in check.lower()

    # Log Supabase (no auth call; client = None uses key)
    try:
        supabase.table("logs").insert(state["log_entry"]).execute()
    except Exception as db_e:
        print(f"Supabase insert failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(state["log_entry"], f)

    return state


# Node: Identifier Tâches (proactif : base + créatives aléatoires)
def identify_tasks(state: AgentState) -> AgentState:
    is_ai = random.choice([True, False])
    state["repo_dir"] = REPO_DIR_AI if is_ai else REPO_DIR_DEV
    state["repo_obj"] = repo_ai if is_ai else repo_dev
    state["sub_agent"] = "AI" if is_ai else "DEV"

    os.chdir(state["repo_dir"])

    issues = [i.title for i in state["repo_obj"].get_issues(state="open")]
    test_output = subprocess.run(
        "pytest -q", shell=True, capture_output=True, text=True
    ).stdout
    failing = [line for line in test_output.splitlines() if "FAILED" in line]
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
        creative_tasks, random.randint(1, 2)
    )  # Proactif: 1-2 créatives
    if state["sub_agent"] == "DEV":
        tasks += ["Générer/update JARVYS_AI et push to appIA"]
    state["task"] = (
        random.choice(tasks) if tasks else "Proactif: Propose new feature architecture"
    )

    state["log_entry"] = {
        **state["log_entry"],
        "task": state["task"],
        "repo": state["sub_agent"],
        "status": "identified",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        supabase.table("logs").insert(state["log_entry"]).execute()
    except Exception as db_e:
        print(f"Supabase insert failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(state["log_entry"], f)

    return state


# Node: Générer Code
def generate_code(state: AgentState) -> AgentState:
    prompt = f"Génère code/fix pour '{state['task']}' sur {state['sub_agent']}. Utilise env/secrets (e.g., SUPABASE_SERVICE_ROLE auth, GCP_SA_JSON cloud). Si générer JARVYS_AI, output pour push appIA."
    state["code_generated"] = query_grok(prompt, state)

    if "générer JARVYS_AI" in state["task"].lower() or state["sub_agent"] == "AI":
        os.chdir(REPO_DIR_AI)
        # Créer la structure si elle n'existe pas
        os.makedirs("src/jarvys_ai", exist_ok=True)
        file_path = f"src/jarvys_ai/generated_{state['task'].replace(' ', '_')}.py"
        with open(file_path, "w") as f:
            f.write(state["code_generated"])
        os.system(
            f"git add . && git commit -m 'Generated by JARVYS_DEV: {state['task']}' && git push origin main"
        )
        os.chdir("/workspaces/appia-dev")

    return state


# Node: Appliquer & Tester
def apply_test(state: AgentState) -> AgentState:
    file_path = f"src/jarvys_{state['sub_agent'].lower()}/updated_{state['task'].replace(' ', '_')}.py"
    with open(file_path, "w") as f:
        f.write(state["code_generated"])

    # Re-fix lint post-génération
    subprocess.run(f"ruff check --fix {file_path}", shell=True)

    state["test_result"] = subprocess.run(
        f"pytest {file_path}", shell=True, capture_output=True, text=True
    ).stdout
    state["log_entry"] = {
        **state["log_entry"],
        "test_result": state["test_result"][:500],
    }
    try:
        supabase.table("logs").update(state["log_entry"]).eq(
            "task", state["task"]
        ).execute()
    except Exception as db_e:
        print(f"Supabase update failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(state["log_entry"], f)

    return state


# Node: Update Docs
def update_docs(state: AgentState) -> AgentState:
    prompt = f"Génère update doc Markdown pour '{state['task']}' sur {state['sub_agent']}. Sections: Description, Changements, Impact, Exemples. Créatif: Ajoute analogies/ideas fun alignées."
    state["doc_update"] = query_grok(prompt, state)

    with open("README.md", "a") as f:
        f.write(
            f"\n## Update: {state['task']} ({time.strftime('%Y-%m-%d')})\n{state['doc_update']}\n"
        )

    os.system("git add README.md")
    state["log_entry"] = {**state["log_entry"], "doc_update": state["doc_update"][:500]}
    try:
        supabase.table("logs").update(state["log_entry"]).eq(
            "task", state["task"]
        ).execute()
    except Exception as db_e:
        print(f"Supabase update failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(state["log_entry"], f)

    return state


# Node: Self-Reflect & Commit/PR
def reflect_commit(state: AgentState) -> AgentState:
    if "FAILED" in state["test_result"]:
        prompt = f"Reflect: Failed '{state['test_result']}'. Improve, créatif/proactif (alt approaches), adaptable (handle unknown)."
        state["reflection"] = query_grok(prompt, state)
        state["log_entry"] = {**state["log_entry"], "reflection": state["reflection"]}
        try:
            supabase.table("logs").update(state["log_entry"]).eq(
                "task", state["task"]
            ).execute()
        except Exception as db_e:
            print(f"Supabase update failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(state["log_entry"], f)
        # FIX: Return state instead of dict
        return state
    else:
        os.system(
            f"git add . && git commit -m 'Grok Auto: {state['task']} with docs' && git push origin grok-evolution"
        )
        pr = state["repo_obj"].create_pull(
            title=f"Grok PR: {state['task']}",
            body=f"Code: {state['code_generated']}\nDocs: {state['doc_update']}\nLog: {str(state['log_entry'])}",
            head="grok-evolution",
            base="main",
        )
        state["log_entry"] = {**state["log_entry"], "pr_url": pr.html_url}

        # Transparence: Créer issue avec full log
        state["repo_obj"].create_issue(
            title=f"Grok Log: {state['task']} Completed", body=str(state["log_entry"])
        )

        state["log_entry"] = {**state["log_entry"], "status": "completed"}
        try:
            supabase.table("logs").update(state["log_entry"]).eq(
                "task", state["task"]
            ).execute()
        except Exception as db_e:
            print(f"Supabase update failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(state["log_entry"], f)

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

# Add conditional edges
graph.add_conditional_edges(
    "reflect_commit",
    lambda s: "generate" if "FAILED" in s["test_result"] else END,
    {"generate": "generate", END: END},
)
graph.add_conditional_edges(
    "fix_lint",
    lambda s: "fix_lint" if not s["lint_fixed"] else "identify",
    {"fix_lint": "fix_lint", "identify": "identify"},
)

orchestrator = graph.compile()


def run_orchestrator():
    state = AgentState(
        task="",
        sub_agent="",
        repo_dir="/workspaces/appia-dev",
        repo_obj=None,
        code_generated="",
        test_result="",
        reflection="",
        doc_update="",
        log_entry={},
        lint_fixed=False,
    )
    max_cycles = 10  # Guard global
    cycle = 0
    while cycle < max_cycles:
        state = orchestrator.invoke(state)
        time.sleep(3600)  # 1h
        cycle += 1


if __name__ == "__main__":
    run_orchestrator()
