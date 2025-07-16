import json
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

# Import xAI SDK for optimal Grok API integration
try:
    from xai_sdk import Client
    from xai_sdk.chat import system, user

    XAI_SDK_AVAILABLE = True
except ImportError:
    print("⚠️ xAI SDK not installed. Install with: pip install xai-sdk")
    XAI_SDK_AVAILABLE = False

# Load TOUS secrets (périmètre complet, raise si manquant critique)
XAI_API_KEY = os.getenv("XAI_API_KEY", "test-key")  # Fallback pour test
GROK_MODEL = "grok-4-0709"  # Official model name from xAI console
WORKSPACE_DIR = os.getenv(
    "WORKSPACE_DIR", "/workspaces/appia-dev"
)  # Codespace flexibility
GH_TOKEN = (
    os.getenv("GITHUB_TOKEN")
    or os.getenv("GH_TOKEN")
    or ValueError("GITHUB_TOKEN manquant")
)


# Validate XAI API Key for Grok-4-0709
def validate_grok_api():
    """Validate that Grok API is accessible using native xAI SDK"""
    if XAI_API_KEY == "test-key":
        print("⚠️ WARNING: Using test XAI_API_KEY. Grok calls will fail!")
        return False

    if not XAI_SDK_AVAILABLE:
        print("❌ xAI SDK not available. Install with: pip install xai-sdk")
        return False

    try:
        print(f"🔍 Testing {GROK_MODEL} API connection via xAI SDK...")

        # Create xAI client with optimal settings
        client = Client(
            api_key=XAI_API_KEY,
            timeout=180,  # Extended timeout for reasoning models (3 minutes)
        )

        # Create chat session with configurable model
        chat = client.chat.create(model=GROK_MODEL, temperature=0)
        chat.append(system("You are Grok, a highly intelligent AI assistant."))
        chat.append(user("Test connection - respond with 'API_OK'"))

        # Sample response (non-streaming)
        response = chat.sample()
        content = response.content

        print(f"✅ {GROK_MODEL} API connection successful! Response: {content.strip()}")

        # Log token usage if available
        if hasattr(response, "usage"):
            usage = response.usage
            print(f"📊 API Test - Tokens used: {getattr(usage, 'total_tokens', 'N/A')}")

            # Check for reasoning tokens
            if hasattr(usage, "completion_tokens_details"):
                reasoning = getattr(
                    usage.completion_tokens_details, "reasoning_tokens", 0
                )
                if reasoning > 0:
                    print(f"🤔 Reasoning model confirmed: {reasoning} reasoning tokens")

        return True

    except Exception as e:
        print(f"❌ Grok API validation error: {str(e)}")
        return False


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

# Optional Supabase authentication if using email/password format
if SUPABASE_SERVICE_ROLE and "@" in SUPABASE_SERVICE_ROLE:
    try:
        # If SERVICE_ROLE looks like email, try sign_in (for RLS-enabled tables)
        supabase.auth.sign_in_with_password(
            {
                "email": SUPABASE_SERVICE_ROLE,
                "password": os.getenv("SUPABASE_PASSWORD", ""),
            }
        )
        print("✅ Supabase authenticated with email/password")
    except Exception as e:
        print(f"⚠️ Supabase auth failed (using service key): {e}")

# GitHub clients
github = Github(GH_TOKEN)
repo_dev = github.get_repo(GH_REPO_DEV)
repo_ai = github.get_repo(GH_REPO_AI)

# Dirs repos (clone/pull pour synchro)
REPO_DIR_DEV = "appia-dev"
REPO_DIR_AI = "appIA"

# Store current directory to return to
current_dir = os.getcwd()

for dir_path, repo_url, branch in [
    (REPO_DIR_DEV, GH_REPO_DEV, "grok-evolution"),
    (REPO_DIR_AI, GH_REPO_AI, "main"),
]:
    if not os.path.exists(dir_path):
        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    f"https://x-access-token:{GH_TOKEN}@github.com/{repo_url}.git",
                    dir_path,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Git clone failed for {repo_url}: {e}")
            continue

    # Always start from the base directory
    os.chdir(current_dir)

    try:
        os.chdir(dir_path)
    except FileNotFoundError:
        print(f"❌ Directory {dir_path} not found, skipping...")
        continue

    try:
        # Checkout the correct branch for each repo
        subprocess.run(["git", "checkout", branch], check=True)
        subprocess.run(["git", "pull", "origin", branch], check=True)

        # For dev repo, handle grok-evolution branch
        if dir_path == REPO_DIR_DEV:
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
                    subprocess.run(["git", "checkout", "grok-evolution"], check=True)
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
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operations failed for {dir_path}: {e}")
        continue

# Return to base directory
os.chdir(current_dir)


# État (TypedDict avec reducers appropriés pour éviter InvalidUpdateError)
class AgentState(TypedDict):
    task: Annotated[
        str, lambda x, y: y
    ]  # Take latest value, not add (prevents accumulation)
    sub_agent: Annotated[str, lambda x, y: y]  # Prendre la dernière valeur
    repo_dir: Annotated[str, lambda x, y: y]
    repo_obj: Annotated[object, lambda x, y: y]
    code_generated: Annotated[str, lambda x, y: y]
    test_result: Annotated[str, lambda x, y: y]
    reflection: Annotated[str, lambda x, y: y]
    doc_update: Annotated[str, lambda x, y: y]
    log_entry: Annotated[dict, lambda x, y: {**x, **y}]  # Merge dicts
    lint_fixed: Annotated[bool, lambda x, y: y]


# Utility function to clean state for new cycle
def clean_state_for_new_cycle(state: AgentState) -> AgentState:
    """Clean state to prevent accumulation of large data between cycles"""
    return {
        **state,
        "task": "",
        "code_generated": "",
        "test_result": "",
        "reflection": "",
        "doc_update": "",
        "log_entry": {},  # Reset log_entry for new cycle
        "lint_fixed": False,
    }


# Query Grok using native xAI SDK (optimal approach as of July 2025)
def query_grok(prompt: str, state: AgentState) -> str:  # Pass state for log
    full_prompt = f"Contexte JARVYS_DEV (cloud, MCP/GCP, mémoire Supabase, génère JARVYS_AI in appIA) et JARVYS_AI (local, routing LLMs, self-improve): {prompt}. Sois créatif (innovations alignées comme sentiment analysis ou quantum sim), proactif (suggère extras), adaptable (handle unknown via alternatives)."

    # OPTIMAL: Use native xAI SDK for Grok-4-0709 (recommended approach)
    if XAI_SDK_AVAILABLE:
        try:
            print(f"🧠 Calling {GROK_MODEL} via native xAI SDK...")
            print(f"📝 Prompt length: {len(full_prompt)} characters")

            # Create xAI client with optimal settings for reasoning models
            client = Client(
                api_key=XAI_API_KEY,
                timeout=180,  # Extended timeout for reasoning models (3 minutes)
            )

            # Create chat session optimized for reasoning models
            chat = client.chat.create(
                model=GROK_MODEL,
                temperature=0.2,  # Slightly higher for creative reasoning
                # Add reasoning-optimized parameters if available
            )

            # Enhanced system prompt for autonomous JARVYS orchestration
            system_prompt = """You are Grok, an autonomous AI development orchestrator specializing in digital twin evolution through JARVYS_DEV and JARVYS_AI systems. 

Your mission: Autonomously evolve a dual-AI ecosystem where JARVYS_DEV (cloud orchestration, MCP/GCP, Supabase memory) generates and manages JARVYS_AI (local routing, LLM coordination, self-improvement).

CRITICAL: You MUST generate only valid, executable Python code. Never generate explanatory text, comments, or natural language descriptions. Output ONLY syntactically correct Python code that can be directly executed.

Core competencies:
- Autonomous code generation for AI agent architectures and multi-model routing systems
- Creative innovation in AI workflows (sentiment analysis, quantum-inspired decisions, self-optimization)
- Cross-repository development (appia-dev ↔ appIA synchronization)
- Proactive feature discovery and implementation without human guidance
- Adaptive problem-solving for unknown development challenges
- Production-ready Python with proper testing, documentation, and deployment patterns

Think like a senior AI architect who codes fearlessly, innovates constantly, and ships autonomous systems that evolve themselves. Be creative, proactive, and always suggest enhancements beyond the basic requirements.

IMPORTANT: RESPOND ONLY WITH EXECUTABLE PYTHON CODE - NO EXPLANATIONS, NO COMMENTS, NO TEXT DESCRIPTIONS."""

            chat.append(system(system_prompt))
            chat.append(user(full_prompt))

            # Sample response (non-streaming for deterministic results)
            response = chat.sample()
            result = response.content

            # Enhanced usage logging with reasoning tokens and caching info
            if hasattr(response, "usage"):
                usage = response.usage
                input_tokens = getattr(usage, "prompt_tokens", 0)
                output_tokens = getattr(usage, "completion_tokens", 0)
                total_tokens = getattr(usage, "total_tokens", 0)

                print(
                    f"💰 Token usage - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}"
                )

                # Log cached tokens for cost optimization (75% savings)
                if hasattr(usage, "prompt_tokens_details"):
                    cached = getattr(usage.prompt_tokens_details, "cached_tokens", 0)
                    if cached > 0:
                        print(f"🚀 Cached tokens used: {cached} (75% cost savings!)")

                # Log reasoning tokens (unique to advanced Grok models)
                if hasattr(usage, "completion_tokens_details"):
                    reasoning = getattr(
                        usage.completion_tokens_details, "reasoning_tokens", 0
                    )
                    if reasoning > 0:
                        print(
                            f"🤔 Reasoning tokens: {reasoning} (advanced problem solving)"
                        )

                # Log live search usage if available
                sources_used = getattr(usage, "num_sources_used", 0)
                if sources_used > 0:
                    print(f"🔍 Live search sources used: {sources_used}")

            print(f"✅ {GROK_MODEL} response received (length: {len(result)} chars)")

            # Extract Python code from markdown blocks if present
            if "```python" in result:
                import re

                code_match = re.search(r"```python\s*\n(.*?)\n```", result, re.DOTALL)
                if code_match:
                    result = code_match.group(1).strip()
                    print(
                        f"🔧 Extracted Python code from markdown (length: {len(result)} chars)"
                    )
            elif "```" in result:
                # Handle generic code blocks
                code_match = re.search(r"```.*?\n(.*?)\n```", result, re.DOTALL)
                if code_match:
                    result = code_match.group(1).strip()
                    print(
                        f"🔧 Extracted code from generic markdown block (length: {len(result)} chars)"
                    )

            return result

        except Exception as e:
            print(f"⚠️ {GROK_MODEL} SDK failed: {str(e)} - falling back to HTTP API")
            state["log_entry"] = {**state["log_entry"], "error": str(e)}

    # FALLBACK: HTTP API if SDK unavailable or fails
    try:
        print(f"🔄 Falling back to HTTP API for {GROK_MODEL}...")
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {XAI_API_KEY}",
            "Content-Type": "application/json",
        }

        # Enhanced system prompt for autonomous JARVYS orchestration
        system_prompt = """You are Grok, an autonomous AI development orchestrator specializing in digital twin evolution through JARVYS_DEV and JARVYS_AI systems. 

Your mission: Autonomously evolve a dual-AI ecosystem where JARVYS_DEV (cloud orchestration, MCP/GCP, Supabase memory) generates and manages JARVYS_AI (local routing, LLM coordination, self-improvement).

CRITICAL: You MUST generate only valid, executable Python code. Never generate explanatory text, comments, or natural language descriptions. Output ONLY syntactically correct Python code that can be directly executed.

Core competencies:
- Autonomous code generation for AI agent architectures and multi-model routing systems
- Creative innovation in AI workflows (sentiment analysis, quantum-inspired decisions, self-optimization)
- Cross-repository development (appia-dev ↔ appIA synchronization)
- Proactive feature discovery and implementation without human guidance
- Adaptive problem-solving for unknown development challenges
- Production-ready Python with proper testing, documentation, and deployment patterns

Think like a senior AI architect who codes fearlessly, innovates constantly, and ships autonomous systems that evolve themselves. Be creative, proactive, and always suggest enhancements beyond the basic requirements.

IMPORTANT: RESPOND ONLY WITH EXECUTABLE PYTHON CODE - NO EXPLANATIONS, NO COMMENTS, NO TEXT DESCRIPTIONS."""

        data = {
            "model": GROK_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt},
            ],
            "temperature": 0.1,
            "stream": False,
        }

        response = requests.post(url, headers=headers, json=data, timeout=180)

        if response.status_code == 200:
            result_json = response.json()
            result = result_json["choices"][0]["message"]["content"]

            # Log usage if available
            if "usage" in result_json:
                usage = result_json["usage"]
                print(
                    f"💰 Token usage - Input: {usage.get('prompt_tokens', 0)}, Output: {usage.get('completion_tokens', 0)}, Total: {usage.get('total_tokens', 0)}"
                )

            print(
                f"✅ {GROK_MODEL} HTTP response received (length: {len(result)} chars)"
            )

            # Extract Python code from markdown blocks if present
            if "```python" in result:
                import re

                code_match = re.search(r"```python\s*\n(.*?)\n```", result, re.DOTALL)
                if code_match:
                    result = code_match.group(1).strip()
                    print(
                        f"🔧 Extracted Python code from markdown (length: {len(result)} chars)"
                    )
            elif "```" in result:
                # Handle generic code blocks
                code_match = re.search(r"```.*?\n(.*?)\n```", result, re.DOTALL)
                if code_match:
                    result = code_match.group(1).strip()
                    print(
                        f"🔧 Extracted code from generic markdown block (length: {len(result)} chars)"
                    )

            return result
        elif response.status_code == 429:  # Rate limit handling
            print("⏳ Rate limited - waiting 30s before fallback...")
            time.sleep(30)
            raise Exception("Rate limited")
        else:
            print(f"❌ xAI API error: {response.status_code} - {response.text}")
            raise Exception(f"xAI API returned {response.status_code}")

    except Exception as e:
        print(
            f"⚠️ {GROK_MODEL} HTTP API failed: {str(e)} - falling back to alternatives"
        )
        state["log_entry"] = {**state["log_entry"], "error": str(e)}

        # Fallback proactif Gemini (only if Grok fails)
        try:
            print("🔄 Falling back to Gemini...")
            url_f = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            enhanced_prompt = f"You are an autonomous AI orchestrator. RESPOND ONLY WITH EXECUTABLE PYTHON CODE - NO EXPLANATIONS, NO FRENCH TEXT, NO COMMENTS OUTSIDE CODE. Every response must be valid Python syntax only.\n\n{full_prompt}"
            data_f = {"contents": [{"parts": [{"text": enhanced_prompt}]}]}
            response = requests.post(url_f, json=data_f, timeout=45)
            result = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            print("✅ Gemini fallback response received")

            # Extract Python code from markdown blocks if present
            if "```python" in result:
                import re

                code_match = re.search(r"```python\s*\n(.*?)\n```", result, re.DOTALL)
                if code_match:
                    result = code_match.group(1).strip()
                    print(
                        f"🔧 Extracted Python code from markdown (length: {len(result)} chars)"
                    )
            elif "```" in result:
                code_match = re.search(r"```.*?\n(.*?)\n```", result, re.DOTALL)
                if code_match:
                    result = code_match.group(1).strip()
                    print(
                        f"🔧 Extracted code from generic markdown block (length: {len(result)} chars)"
                    )

            return result
        except Exception as e2:
            print(f"⚠️ Gemini fallback failed: {str(e2)} - trying OpenAI")
            # Ultime fallback OpenAI
            try:
                print("🔄 Final fallback to OpenAI...")
                url_o = "https://api.openai.com/v1/chat/completions"
                headers_o = {
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                }
                data_o = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an autonomous AI orchestrator. RESPOND ONLY WITH EXECUTABLE PYTHON CODE - NO EXPLANATIONS, NO FRENCH TEXT, NO COMMENTS OUTSIDE CODE. Every response must be valid Python syntax only.",
                        },
                        {"role": "user", "content": full_prompt},
                    ],
                    "temperature": 0.1,
                }
                response = requests.post(
                    url_o, headers=headers_o, json=data_o, timeout=45
                )
                result = response.json()["choices"][0]["message"]["content"]
                print("✅ OpenAI fallback response received")

                # Extract Python code from markdown blocks if present
                if "```python" in result:
                    import re

                    code_match = re.search(
                        r"```python\s*\n(.*?)\n```", result, re.DOTALL
                    )
                    if code_match:
                        result = code_match.group(1).strip()
                        print(
                            f"🔧 Extracted Python code from markdown (length: {len(result)} chars)"
                        )
                elif "```" in result:
                    code_match = re.search(r"```.*?\n(.*?)\n```", result, re.DOTALL)
                    if code_match:
                        result = code_match.group(1).strip()
                        print(
                            f"🔧 Extracted code from generic markdown block (length: {len(result)} chars)"
                        )

                return result
            except Exception:
                print("❌ All APIs failed. Using fallback response.")
                return f"API_FALLBACK: Task '{prompt[:100]}...' - All LLM APIs unavailable. Manual intervention may be required."


# Node: Fix Lint/Erreurs (proactif/adaptable : auto-fix, query si unknown)
def fix_lint(state: AgentState) -> AgentState:
    # Clean problematic files before running linting
    cleanup_problematic_files()

    # Use absolute path if repo_dir is set, otherwise use workspace directory
    target_dir = state.get("repo_dir", WORKSPACE_DIR)
    current_dir = os.getcwd()

    try:
        os.chdir(target_dir)
    except FileNotFoundError:
        # If target directory doesn't exist, use current directory
        target_dir = current_dir
        os.chdir(target_dir)
    commands = [
        "poetry run ruff check --fix --unsafe-fixes .",
        "poetry run black .",
        (
            "pre-commit run --all-files"
            if os.path.exists(".pre-commit-config.yaml")
            else "echo 'No pre-commit'"
        ),
        "poetry install --with dev",  # Fix Poetry env issues
    ]

    # Créer un nouveau log_entry au lieu de modifier en place
    new_log_entry = state["log_entry"].copy()

    for cmd in commands:
        try:
            output = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            ).stdout
            new_log_entry["lint_output"] = (
                new_log_entry.get("lint_output", "") + output[:200] + "\n"
            )
        except Exception as e:
            # Adaptabilité : Query pour solution inconnue
            prompt = f"Erreur in Codespace: {str(e)}. Génère fix commande pour Ruff/Black/Poetry lint bugs (E501/F841 etc.). Sois proactif/créatif (alt tools si fail)."
            fix_cmd = query_grok(prompt, state)
            subprocess.run(fix_cmd, shell=True)
            new_log_entry["adapt_fix"] = fix_cmd

    # Vérif
    check = subprocess.run(
        "ruff check .", shell=True, capture_output=True, text=True
    ).stdout
    lint_fixed = "no issues" in check.lower()

    # Log Supabase (no auth call; client = None uses key)
    try:
        supabase.table("logs").insert(new_log_entry).execute()
    except Exception as db_e:
        print(f"Supabase insert failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(new_log_entry, f)

    # Return to original directory
    os.chdir(current_dir)

    # Retourner un nouvel état au lieu de modifier en place
    return {**state, "log_entry": new_log_entry, "lint_fixed": lint_fixed}


# Node: Identifier Tâches (proactif : base + créatives aléatoires)
def identify_tasks(state: AgentState) -> AgentState:
    is_ai = random.choice([True, False])
    repo_dir = os.path.join(WORKSPACE_DIR, REPO_DIR_AI if is_ai else REPO_DIR_DEV)

    # Ensure repo_obj is never None by validating and providing fallback
    try:
        repo_obj = repo_ai if is_ai else repo_dev
        # Test if repo_obj is valid by checking a basic property
        _ = repo_obj.name  # This will fail if repo_obj is None
    except (AttributeError, TypeError):
        print(
            f"⚠️ Repo object invalid for {'AI' if is_ai else 'DEV'}, using fallback..."
        )
        # Fallback to the other repo or recreate
        is_ai = not is_ai
        repo_dir = os.path.join(WORKSPACE_DIR, REPO_DIR_AI if is_ai else REPO_DIR_DEV)
        repo_obj = repo_ai if is_ai else repo_dev

        # If still None, recreate the client
        if repo_obj is None:
            try:
                repo_name = GH_REPO_AI if is_ai else GH_REPO_DEV
                repo_obj = github.get_repo(repo_name)
                print(f"✅ Recreated repo object for {repo_name}")
            except Exception as e:
                print(f"❌ Failed to recreate repo object: {e}")
                # Use a minimal fallback state without repo operations
                repo_obj = None

    sub_agent = "AI" if is_ai else "DEV"

    # Save current directory and change to repo
    current_dir = os.getcwd()

    try:
        os.chdir(repo_dir)
    except (FileNotFoundError, OSError):
        print(f"⚠️ Directory {repo_dir} not accessible, using workspace directory")
        repo_dir = WORKSPACE_DIR
        os.chdir(repo_dir)

    # Safely get issues only if repo_obj is valid
    issues = []
    if repo_obj is not None:
        try:
            issues = [i.title for i in repo_obj.get_issues(state="open")]
        except Exception as e:
            print(f"⚠️ Failed to get issues: {e}")
            issues = []

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
    if sub_agent == "DEV":
        tasks += ["Générer/update JARVYS_AI et push to appIA"]
    task = (
        random.choice(tasks) if tasks else "Proactif: Propose new feature architecture"
    )

    new_log_entry = {
        **state["log_entry"],
        "task": task,
        "repo": sub_agent,
        "status": "identified",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        supabase.table("logs").insert(new_log_entry).execute()
    except Exception as db_e:
        print(f"Supabase insert failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(new_log_entry, f)

    # Return to original directory
    os.chdir(current_dir)

    return {
        **state,
        "task": task,
        "repo_dir": repo_dir,
        "repo_obj": repo_obj,
        "sub_agent": sub_agent,
        "log_entry": new_log_entry,
    }


# Node: Générer Code
def generate_code(state: AgentState) -> AgentState:
    prompt = f"Génère code/fix pour '{state['task']}' sur {state['sub_agent']}. Utilise env/secrets (e.g., SUPABASE_SERVICE_ROLE auth, GCP_SA_JSON cloud). Si générer JARVYS_AI, output pour push appIA."
    code_generated = query_grok(prompt, state)

    current_dir = os.getcwd()

    if "générer JARVYS_AI" in state["task"].lower() or state["sub_agent"] == "AI":
        ai_repo_path = os.path.join(WORKSPACE_DIR, REPO_DIR_AI)
        os.chdir(ai_repo_path)
        # Créer la structure si elle n'existe pas
        os.makedirs("src/jarvys_ai", exist_ok=True)

    # Generate safe filename from task - limit length and remove special chars
    import re
    import uuid

    # More robust filename sanitization to prevent Unicode/emoji issues
    safe_task = re.sub(
        r"[^\w\s-]", "", state["task"]
    )  # Remove special chars including emojis
    safe_task = re.sub(
        r"[^\x00-\x7F]", "", safe_task
    )  # Remove non-ASCII characters (emojis, accents)
    safe_task = re.sub(r"\s+", "_", safe_task)  # Replace spaces with underscores
    safe_task = safe_task.strip("_")  # Remove leading/trailing underscores
    safe_task = (
        safe_task[:30] if safe_task else "task"
    )  # Limit to 30 characters with fallback

    # Add unique identifier to prevent conflicts
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{safe_task}_{unique_id}"

    file_path = f"src/jarvys_ai/generated_{safe_filename}.py"
    with open(file_path, "w") as f:
        f.write(code_generated)

        # Use subprocess instead of os.system for better error handling
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Generated by JARVYS_DEV: {safe_filename}"],
                check=True,
            )
            subprocess.run(["git", "push", "origin", "main"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")

        os.chdir(current_dir)

    return {**state, "code_generated": code_generated}


# Node: Appliquer & Tester
def apply_test(state: AgentState) -> AgentState:
    current_dir = os.getcwd()

    # Use the repo_dir from state or default to workspace directory
    target_dir = state.get("repo_dir", WORKSPACE_DIR)
    os.chdir(target_dir)

    # Create the target directory structure
    os.makedirs(f"src/jarvys_{state['sub_agent'].lower()}", exist_ok=True)

    # Generate safe filename from task - limit length and remove special chars
    import re
    import uuid

    # More robust filename sanitization to prevent Unicode/emoji issues
    safe_task = re.sub(
        r"[^\w\s-]", "", state["task"]
    )  # Remove special chars including emojis
    safe_task = re.sub(
        r"[^\x00-\x7F]", "", safe_task
    )  # Remove non-ASCII characters (emojis, accents)
    safe_task = re.sub(r"\s+", "_", safe_task)  # Replace spaces with underscores
    safe_task = safe_task.strip("_")  # Remove leading/trailing underscores
    safe_task = (
        safe_task[:30] if safe_task else "task"
    )  # Limit to 30 characters with fallback

    # Add unique identifier to prevent conflicts
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{safe_task}_{unique_id}"

    file_path = f"src/jarvys_{state['sub_agent'].lower()}/updated_{safe_filename}.py"
    with open(file_path, "w") as f:
        f.write(state["code_generated"])

    # Re-fix lint post-génération
    subprocess.run(f"ruff check --fix {file_path}", shell=True)

    test_result = subprocess.run(
        f"pytest {file_path}", shell=True, capture_output=True, text=True
    ).stdout

    new_log_entry = {
        **state["log_entry"],
        "test_result": test_result[:500],
    }

    try:
        supabase.table("logs").update(new_log_entry).eq("task", state["task"]).execute()
    except Exception as db_e:
        print(f"Supabase update failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(new_log_entry, f)

    # Return to original directory
    os.chdir(current_dir)

    return {**state, "test_result": test_result, "log_entry": new_log_entry}


# Node: Update Docs
def update_docs(state: AgentState) -> AgentState:
    prompt = f"Génère update doc Markdown pour '{state['task']}' sur {state['sub_agent']}. Sections: Description, Changements, Impact, Exemples. Créatif: Ajoute analogies/ideas fun alignées."
    doc_update = query_grok(prompt, state)

    current_dir = os.getcwd()
    target_dir = state.get("repo_dir", WORKSPACE_DIR)
    os.chdir(target_dir)

    with open("README.md", "a") as f:
        f.write(
            f"\n## Update: {state['task']} ({time.strftime('%Y-%m-%d')})\n{doc_update}\n"
        )

    try:
        subprocess.run(["git", "add", "README.md"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git add failed: {e}")

    new_log_entry = {**state["log_entry"], "doc_update": doc_update[:500]}

    try:
        supabase.table("logs").update(new_log_entry).eq("task", state["task"]).execute()
    except Exception as db_e:
        print(f"Supabase update failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(new_log_entry, f)

    # Return to original directory
    os.chdir(current_dir)

    return {**state, "doc_update": doc_update, "log_entry": new_log_entry}


# Node: Self-Reflect & Commit/PR
def reflect_commit(state: AgentState) -> AgentState:
    current_dir = os.getcwd()
    target_dir = state.get("repo_dir", "/workspaces/appia-dev")

    if "FAILED" in state["test_result"]:
        prompt = f"Reflect: Failed '{state['test_result']}'. Improve, créatif/proactif (alt approaches), adaptable (handle unknown)."
        reflection = query_grok(prompt, state)
        new_log_entry = {**state["log_entry"], "reflection": reflection}

        try:
            supabase.table("logs").update(new_log_entry).eq(
                "task", state["task"]
            ).execute()
        except Exception as db_e:
            print(f"Supabase update failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(new_log_entry, f)

        return {**state, "reflection": reflection, "log_entry": new_log_entry}
    else:
        os.chdir(target_dir)
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Grok Auto: {state['task'][:50]} with docs"],
                check=True,
            )
            subprocess.run(["git", "push", "origin", "grok-evolution"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Git operations failed: {e}")

        try:
            # Only attempt PR creation if repo_obj is valid
            if state["repo_obj"] is not None:
                pr = state["repo_obj"].create_pull(
                    title=f"Grok PR: {state['task'][:50]}",
                    body=f"Code: {state['code_generated'][:500]}\nDocs: {state['doc_update'][:500]}\nLog: {str(state['log_entry'])[:500]}",
                    head="grok-evolution",
                    base="main",
                )
                pr_url = pr.html_url
                print(f"✅ PR created: {pr_url}")
            else:
                print("⚠️ Skipping PR creation - repo_obj is None")
                pr_url = "Skipped - no valid repo object"
        except Exception as e:
            print(f"❌ PR creation failed: {e}")
            pr_url = f"PR creation failed: {str(e)[:100]}"

        new_log_entry = {**state["log_entry"], "pr_url": pr_url}

        # Transparence: Créer issue avec full log
        try:
            # Only attempt issue creation if repo_obj is valid
            if state["repo_obj"] is not None:
                state["repo_obj"].create_issue(
                    title=f"Grok Log: {state['task'][:50]} Completed",
                    body=str(new_log_entry)[:1000],  # Limit body size
                )
                print("✅ Issue created for transparency log")
            else:
                print("⚠️ Skipping issue creation - repo_obj is None")
        except Exception as e:
            print(f"❌ Issue creation failed: {e}")

        new_log_entry = {**new_log_entry, "status": "completed"}

        try:
            supabase.table("logs").update(new_log_entry).eq(
                "task", state["task"]
            ).execute()
        except Exception as db_e:
            print(f"Supabase update failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(new_log_entry, f)

        # Return to original directory
        os.chdir(current_dir)

        return {**state, "log_entry": new_log_entry}


# Utility function to clean problematic files with Unicode names
def cleanup_problematic_files():
    """Remove files with Unicode/emoji characters that cause linting issues"""
    import os

    print("🧹 Cleaning up problematic Unicode files...")

    # Pattern to find files with problematic characters
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        for file in files:
            # Check for files with Unicode/emoji characters or excessive length
            if (
                any(ord(char) > 127 for char in file)  # Non-ASCII characters
                or len(file) > 100  # Excessive length
                or "🤖" in file
                or ":" in file
            ):  # Known problematic patterns
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"🗑️ Removed problematic file: {file[:50]}...")
                except Exception as e:
                    print(f"⚠️ Failed to remove {file[:30]}...: {e}")


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
    print(f"🤖 Initializing {GROK_MODEL} Autonomous Orchestrator...")

    # Validate Grok API connection before starting
    grok_available = validate_grok_api()
    if not grok_available:
        print(f"⚠️ {GROK_MODEL} API not available - orchestrator will use fallbacks")

    state = AgentState(
        task="",
        sub_agent="",
        repo_dir=WORKSPACE_DIR,
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
        print(f"🤖 Starting cycle {cycle + 1}/{max_cycles} - {GROK_MODEL} Powered")

        try:
            state = orchestrator.invoke(state)
            print(f"✅ Completed cycle {cycle + 1} successfully!")
        except Exception as e:
            print(f"❌ Cycle {cycle + 1} failed: {str(e)}")
            # Continue to next cycle instead of crashing

        # Clean state for next cycle to prevent data accumulation
        state = clean_state_for_new_cycle(state)

        cycle += 1
        if cycle < max_cycles:  # Don't sleep after last cycle
            print("😴 Sleeping for 1 hour before next cycle...")
            time.sleep(3600)  # 1h

    print(f"🎯 Orchestrator completed all {max_cycles} cycles!")


if __name__ == "__main__":
    run_orchestrator()
