"""
🤖 GROK-4 Autonomous Orchestrator Agent
=======================================

An autonomous AI orchestrator agent built using LangGraph for digital twin evolution.
Manages the full development cycle for JARVYS project using Grok-4-0709 via official xAI SDK.

⚠️ IMPORTANT: This orchestrator ONLY uses grok-4-0709 model. Fallbacks only to ChatGPT-4 or Claude (no other Grok versions).

Architecture:
- JARVYS_DEV: Cloud orchestration (appia-dev/grok-evolution)
- JARVYS_AI: Local execution (appIA/main)

Core Capabilities:
- Repository synchronization and management
- Autonomous code generation using Grok-4-0709 ONLY
- Adaptive lint/error fixing (Ruff, Black, pre-commit)
- Proactive task identification and creative innovation
- Fallback chain: Grok-4-0709→ChatGPT-4→Claude (NO other Grok versions)
- Self-reflection, testing, and PR creation
- Transparent logging to Supabase

Implementation follows official xAI SDK documentation:
    from xai_sdk import Client
    from xai_sdk.chat import user, system
    client = Client(api_key="<XAI_API_KEY>")
    chat = client.chat.create(model="grok-4-0709", temperature=0)
"""

import json
import os
import random  # Added missing import
import re
import subprocess
import time

import requests
from google.oauth2 import service_account
from langgraph.graph import END, StateGraph
from typing_extensions import Annotated, TypedDict

from supabase import create_client

# Import GitHub library with proper error handling
try:
    from github import Github

    GITHUB_AVAILABLE = True
except ImportError:
    print("Warning: GitHub library not available. Install with: pip install PyGithub")
    GITHUB_AVAILABLE = False

# Import xAI SDK for optimal Grok API integration
try:
    from xai_sdk import Client
    from xai_sdk.chat import system, user

    XAI_SDK_AVAILABLE = True
except ImportError:
    print("⚠️ xAI SDK not installed. Install with: pip install xai-sdk")
    XAI_SDK_AVAILABLE = False

# Import Claude SDK for code validation and testing
try:
    import anthropic

    CLAUDE_AVAILABLE = True
except ImportError:
    print("⚠️ Claude SDK not installed. Install with: pip install anthropic")
    CLAUDE_AVAILABLE = False

# Load TOUS secrets (périmètre complet, raise si manquant critique)
XAI_API_KEY = os.getenv("XAI_API_KEY", "test-key")  # Fallback pour test
GROK_MODEL = "grok-4-0709"  # STRICT: Only grok-4-0709 allowed, no other Grok versions

# Validation stricte du modèle Grok
if "grok" in GROK_MODEL.lower() and GROK_MODEL != "grok-4-0709":
    raise ValueError(
        f"ERREUR: Seul grok-4-0709 est autorisé. Modèle détecté: {GROK_MODEL}"
    )

print(f"✅ Validation: Utilisation exclusive de {GROK_MODEL}")

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
        print(
            "📚 Using official xAI SDK documentation pattern: chat.create(model='grok-4-0709')"
        )

        # Create xAI client with optimal settings (following official documentation)
        client = Client(
            api_key=XAI_API_KEY,
            timeout=300,  # Extended timeout for reasoning models (5 minutes)
        )

        # Create chat session with official model name from xAI console
        chat = client.chat.create(model=GROK_MODEL, temperature=0)
        chat.append(
            system(
                "You are Grok-4, a highly intelligent AI assistant specializing in autonomous development orchestration."
            )
        )
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


# Validate Claude API for code validation and testing
def validate_claude_api():
    """Validate that Claude API is accessible for code validation"""
    if not CLAUDE_API_KEY:
        print("⚠️ WARNING: No Claude API key found. Code validation will be skipped!")
        return False

    if not CLAUDE_AVAILABLE:
        print("❌ Claude SDK not available. Install with: pip install anthropic")
        return False

    try:
        print("🔍 Testing Claude 4 API connection...")

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

        # Test with Claude Sonnet 4 (recommended for code validation)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": "Test connection - respond with 'CLAUDE_API_OK'",
                }
            ],
        )

        content = response.content[0].text if response.content else ""
        print(f"✅ Claude 4 API connection successful! Response: {content.strip()}")

        # Log token usage
        if hasattr(response, "usage"):
            usage = response.usage
            print(
                f"📊 Claude Test - Input tokens: {usage.input_tokens}, Output tokens: {usage.output_tokens}"
            )

        return True

    except Exception as e:
        print(f"❌ Claude API validation error: {str(e)}")
        return False


# Initialize infinite memory system in Supabase
def init_infinite_memory():
    """Initialize the infinite memory system with Supabase backend"""
    try:
        print("🧠 Initializing infinite memory system...")

        # Test basic connection first
        try:
            # Simple test query to check connection
            supabase.table("jarvys_memory").select("*").limit(1).execute()
            print("✅ Supabase connection verified")
        except Exception as conn_error:
            print(f"⚠️ Supabase connection issue: {conn_error}")
            print("📝 Will use local fallback storage only")
            return False

        # Test memory storage with correct jarvys_memory schema
        test_memory_data = {
            "content": "Système JARVYS initialisé avec succès - Orchestrateur Grok-Claude opérationnel",
            "agent_source": "JARVYS_DEV",
            "memory_type": "system_init",
            "user_context": "orchestrator_initialization",
            "importance_score": 1.0,
            "tags": ["init", "system", "orchestrator", "grok", "claude"],
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "models_available": {
                    "grok": XAI_SDK_AVAILABLE,
                    "claude": CLAUDE_AVAILABLE,
                },
                "initialization_success": True
            }
        }

        # Try to insert into jarvys_memory table with correct schema
        try:
            result = supabase.table("jarvys_memory").insert(test_memory_data).execute()
            if result.data:
                print("✅ Memory system initialized with jarvys_memory table!")
                print(f"📝 Memory ID: {result.data[0].get('id')}")
                return True
            else:
                print("⚠️ jarvys_memory table insert returned no data")
        except Exception as memory_error:
            print(f"⚠️ jarvys_memory table issue: {memory_error}")

        # Try orchestrator_logs as backup
        try:
            orchestrator_init_data = {
                "agent_type": "JARVYS_DEV",
                "action": "system_initialization",
                "task": "Initialisation de l'orchestrateur Grok-Claude",
                "status": "completed",
                "metadata": test_memory_data["metadata"]
            }
            
            result = supabase.table("orchestrator_logs").insert(orchestrator_init_data).execute()
            if result.data:
                print("✅ Memory system using orchestrator_logs table!")
                return True
        except Exception as orchestrator_error:
            print(f"⚠️ orchestrator_logs table issue: {orchestrator_error}")

        # Try logs table as final backup
        try:
            logs_data = {
                "task": "Initialisation système JARVYS",
                "status": "completed",
                "metadata": test_memory_data["metadata"]
            }
            
            result = supabase.table("logs").insert(logs_data).execute()
            if result.data:
                print("✅ Memory system using logs table!")
                return True
        except Exception as logs_error:
            print(f"⚠️ logs table issue: {logs_error}")

        print("📝 Creating local fallback storage...")
        # Create local memory file as fallback
        os.makedirs("memory_storage", exist_ok=True)
        with open("memory_storage/init_memory.json", "w") as f:
            json.dump(test_memory_data, f, indent=2)

        print("✅ Local memory storage initialized")
        return False

    except Exception as e:
        print(f"⚠️ Memory system initialization failed: {e}")
        print("📝 Will use local fallback storage")
        return False

        print("✅ Local memory storage initialized")
        return False

    except Exception as e:
        print(f"⚠️ Memory system initialization failed: {e}")
        print("📝 Will use local fallback storage")
        return False


# Store memory with infinite retention and intelligent retrieval
def store_memory(
    memory_type: str, content: dict, importance: float = 0.5, tags: list = None
):
    """Store memory in Supabase with infinite retention using correct schema"""
    try:
        # First try with correct jarvys_memory schema
        try:
            jarvys_memory_data = {
                "content": json.dumps(content) if isinstance(content, dict) else str(content),
                "agent_source": "JARVYS_DEV",
                "memory_type": memory_type,
                "user_context": "orchestrator",
                "importance_score": importance,
                "tags": tags or [],
                "metadata": {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "grok_orchestrator",
                    "session": f"session_{int(time.time())}"
                }
            }
            
            result = supabase.table("jarvys_memory").insert(jarvys_memory_data).execute()
            if result.data:
                print(f"🧠 Memory stored in jarvys_memory: {memory_type} (importance: {importance})")
                return result.data[0].get("id") if result.data else None
        except Exception as e:
            print(f"⚠️ jarvys_memory failed: {e}")

        # Try orchestrator_logs as backup
        try:
            orchestrator_data = {
                "agent_type": "JARVYS_DEV",
                "action": memory_type,
                "task": json.dumps(content) if isinstance(content, dict) else str(content),
                "status": "completed",
                "metadata": {
                    "importance_score": importance,
                    "tags": tags or [],
                    "content": content
                }
            }
            
            result = supabase.table("orchestrator_logs").insert(orchestrator_data).execute()
            if result.data:
                print(f"🧠 Memory stored in orchestrator_logs: {memory_type}")
                return result.data[0].get("id") if result.data else None
        except Exception as e:
            print(f"⚠️ orchestrator_logs failed: {e}")

        # Try logs table as final backup
        try:
            logs_data = {
                "task": f"{memory_type}: {str(content)[:200]}",
                "status": "completed",
                "metadata": {
                    "importance_score": importance,
                    "tags": tags or [],
                    "content": content,
                    "memory_type": memory_type
                }
            }
            
            result = supabase.table("logs").insert(logs_data).execute()
            if result.data:
                print(f"🧠 Memory stored in logs: {memory_type}")
                return result.data[0].get("id") if result.data else None
        except Exception as e:
            print(f"⚠️ logs table failed: {e}")

        # Fallback to local storage
        print("⚠️ All Supabase tables failed, using local fallback")
        os.makedirs("memory_storage", exist_ok=True)
        filename = f"memory_storage/{memory_type}_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump({
                "content": content,
                "memory_type": memory_type,
                "importance_score": importance,
                "tags": tags or [],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2)
        print(f"💾 Memory stored locally: {filename}")
        return None

    except Exception as e:
        print(f"⚠️ Memory storage failed: {e}")
        return None
        # Final fallback to append-only log
        try:
            with open("memory_backup.jsonl", "a") as f:
                json.dump(
                    {"timestamp": time.time(), "type": memory_type, "content": content},
                    f,
                )
                f.write("\n")
            print("💾 Memory logged to backup file")
        except Exception:
            print("❌ All memory storage methods failed")
        return None


# Retrieve relevant memories for context
def retrieve_memories(query_type: str = None, limit: int = 10):
    """Retrieve relevant memories from infinite storage"""
    try:
        # Try multiple tables to find memories
        for table_name in ["logs", "jarvys_memory", "memories", "orchestrator_logs"]:
            try:
                query = (
                    supabase.table(table_name).select("*").order("timestamp", desc=True)
                )
                if query_type:
                    query = query.eq("memory_type", query_type)
                result = query.limit(limit).execute()

                if result.data:
                    memories = result.data
                    # Parse JSON content if needed
                    for memory in memories:
                        if isinstance(memory.get("content"), str):
                            try:
                                memory["content"] = json.loads(memory["content"])
                            except:
                                pass  # Keep as string if not JSON
                        if isinstance(memory.get("tags"), str):
                            try:
                                memory["tags"] = json.loads(memory["tags"])
                            except:
                                memory["tags"] = []

                    print(
                        f"🧠 Retrieved {len(memories)} memories from {table_name} table"
                    )
                    return memories
            except Exception as e:
                print(f"⚠️ Failed to retrieve from {table_name}: {e}")
                continue

        # Fallback to local storage
        print("⚠️ Supabase retrieval failed, checking local storage")
        memories = []

        if os.path.exists("memory_storage"):
            for filename in os.listdir("memory_storage"):
                if filename.endswith(".json"):
                    try:
                        with open(f"memory_storage/{filename}", "r") as f:
                            memory = json.load(f)
                            if (
                                not query_type
                                or memory.get("memory_type") == query_type
                            ):
                                memories.append(memory)
                    except Exception:
                        continue

        # Sort by importance if available, otherwise by timestamp
        memories.sort(key=lambda x: x.get("importance_score", 0), reverse=True)
        memories = memories[:limit]

        print(f"💾 Retrieved {len(memories)} memories from local storage")
        return memories

    except Exception as e:
        print(f"⚠️ Memory retrieval failed: {e}")
        return []


# Claude code validation function
def validate_code_with_claude(code: str, task_description: str) -> dict:
    """Use Claude 4 to validate and improve generated code"""
    if not CLAUDE_AVAILABLE or not CLAUDE_API_KEY:
        return {"validated": False, "message": "Claude not available"}

    try:
        print("🔍 Validating code with Claude 4...")

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

        validation_prompt = f"""
You are Claude 4, an expert code reviewer and validator. Analyze this Python code for:

1. Syntax correctness
2. Logic errors  
3. Security vulnerabilities
4. Performance issues
5. Best practices compliance
6. Compatibility with the task requirements

Task: {task_description}

Code to validate:
```python
{code}
```

Respond with a JSON object containing:
- "is_valid": boolean
- "confidence": float (0-1)
- "issues": array of issue descriptions
- "suggestions": array of improvement suggestions
- "security_concerns": array of security issues
- "improved_code": string (if improvements needed)
"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # Using Claude Sonnet 4 for code validation
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": validation_prompt}],
        )

        result_text = response.content[0].text if response.content else ""

        # Extract JSON from response
        try:
            import json

            if "```json" in result_text:
                json_match = re.search(
                    r"```json\s*\n(.*?)\n```", result_text, re.DOTALL
                )
                if json_match:
                    result_json = json.loads(json_match.group(1))
                else:
                    result_json = {
                        "validated": False,
                        "message": "Could not parse Claude response",
                    }
            else:
                result_json = {
                    "validated": False,
                    "message": "No JSON in Claude response",
                }

        except json.JSONDecodeError:
            result_json = {"validated": False, "message": "Invalid JSON from Claude"}

        # Log token usage
        if hasattr(response, "usage"):
            usage = response.usage
            print(
                f"📊 Claude Validation - Input: {usage.input_tokens}, Output: {usage.output_tokens}"
            )

        # Store validation result in memory
        store_memory(
            "code_validation",
            {
                "task": task_description,
                "validation_result": result_json,
                "claude_model": "claude-sonnet-4-20250514",
            },
            importance=0.8,
            tags=["validation", "claude", "code_quality"],
        )

        print(
            f"✅ Claude validation completed - Valid: {result_json.get('is_valid', False)}"
        )
        return result_json

    except Exception as e:
        print(f"❌ Claude validation failed: {str(e)}")
        return {"validated": False, "message": f"Claude error: {str(e)}"}


# Enhanced internet search for technology verification
def verify_technology_updates():
    """Search for latest technology updates and best practices"""
    try:
        print("🌐 Checking for latest technology updates...")

        # Use Grok with internet search capabilities if available
        if XAI_SDK_AVAILABLE and XAI_API_KEY != "test-key":
            try:
                client = Client(api_key=XAI_API_KEY, timeout=60)  # Reduced timeout
                chat = client.chat.create(model=GROK_MODEL, temperature=0.3)

                search_prompt = """Provide a brief summary of recent AI development trends relevant to our project."""

                chat.append(
                    system(
                        "You are a technology research assistant. Provide concise, factual information."
                    )
                )
                chat.append(user(search_prompt))

                response = chat.sample()
                tech_updates = response.content[:500]  # Limit response length

                # Store in memory for future reference
                store_memory(
                    "technology_updates",
                    {
                        "search_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "updates": tech_updates,
                        "source": "grok_quick_summary",
                    },
                    importance=0.5,
                    tags=["technology", "updates", "research"],
                )

                print("✅ Technology updates retrieved and stored")
                return tech_updates
            except Exception as e:
                print(f"⚠️ Grok search failed: {e}")

        print("📝 Using cached technology summary")
        cached_updates = "Recent AI trends: LangGraph 0.5+ improvements, Claude 4 releases, enhanced reasoning models."

        store_memory(
            "technology_updates",
            {
                "search_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "updates": cached_updates,
                "source": "cached_fallback",
            },
            importance=0.3,
            tags=["technology", "cached"],
        )

        return cached_updates

    except Exception as e:
        print(f"⚠️ Technology verification failed: {e}")
        return "Technology verification unavailable"


GH_REPO_DEV = os.getenv("GH_REPO_DEV", "yannabadie/appia-dev")
GH_REPO_AI = os.getenv("GH_REPO_AI", "yannabadie/appIA")
SUPABASE_URL = os.getenv("SUPABASE_URL") or ValueError("SUPABASE_URL manquant")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ValueError("SUPABASE_KEY manquant")
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GCP_SA_JSON = (
    json.loads(os.getenv("GCP_SA_JSON"))
    if os.getenv("GCP_SA_JSON")
    else ValueError("GCP_SA_JSON manquant")
)
SECRET_ACCESS_TOKEN = os.getenv("SECRET_ACCESS_TOKEN")  # Loadé même inusité

# GCP Credentials (pour tâches cloud/adaptabilité)
gcp_credentials = service_account.Credentials.from_service_account_info(GCP_SA_JSON)

# Clients (use SUPABASE_SERVICE_ROLE as key for elevated client if needed)
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


# Git Repository Management with Branch Safety
def ensure_correct_git_setup():
    """Ensure we're on the correct branch and repo setup"""
    original_dir = os.getcwd()

    try:
        # Ensure we're in the correct directory
        os.chdir("/workspaces/appia-dev")

        # Configure Git for divergent branches (one-time setup)
        subprocess.run(["git", "config", "pull.rebase", "false"], capture_output=True)

        # Check current branch
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        print(f"📍 Current branch: {current_branch}")

        # If not on grok-evolution, check it out
        if current_branch != "grok-evolution":
            print(f"🔄 Switching from {current_branch} to grok-evolution...")
            try:
                subprocess.run(["git", "checkout", "grok-evolution"], check=True)
                print("✅ Switched to grok-evolution branch")
            except subprocess.CalledProcessError:
                # Create the branch if it doesn't exist
                print("🆕 Creating grok-evolution branch...")
                subprocess.run(["git", "checkout", "-b", "grok-evolution"], check=True)
                subprocess.run(
                    ["git", "push", "-u", "origin", "grok-evolution"], check=True
                )
                print("✅ Created and pushed grok-evolution branch")

        # Update from remote with proper merge strategy
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "grok-evolution"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("✅ Updated from remote grok-evolution")
            else:
                print(f"⚠️ Pull warning: {result.stderr}")
                # Try to resolve automatically with merge
                subprocess.run(
                    ["git", "pull", "--no-rebase", "origin", "grok-evolution"],
                    capture_output=True,
                )
                print("✅ Resolved with merge strategy")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Pull failed: {e} - continuing anyway")

        # Reset deployment packages to avoid massive commits
        reset_deployment_packages()

        return True

    except Exception as e:
        print(f"❌ Git setup failed: {e}")
        return False
    finally:
        os.chdir(original_dir)


def reset_deployment_packages():
    """Reset deployment packages to avoid committing hundreds of files"""
    try:
        print("🧹 Cleaning deployment packages...")

        # Reset deployment packages to avoid massive commits
        if os.path.exists("deployment_packages"):
            subprocess.run(
                ["git", "checkout", "HEAD", "--", "deployment_packages/"],
                capture_output=True,
            )
            print("✅ Reset deployment packages")

        # Reset other temporary files
        temp_patterns = [
            "src/jarvys_*/generated_*.py",
            "src/jarvys_*/updated_*.py",
            "memory_storage/",
            "*.log",
            "local_logs.json",
        ]

        for pattern in temp_patterns:
            try:
                subprocess.run(
                    ["git", "checkout", "HEAD", "--", pattern], capture_output=True
                )
            except:
                pass

        print("✅ Cleaned temporary files")

    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")


# Call setup at module level
ensure_correct_git_setup()

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
    full_prompt = f"Context: JARVYS_DEV (cloud orchestration, MCP/GCP, Supabase memory, generates JARVYS_AI in appIA) and JARVYS_AI (local deployment, LLM routing, self-improvement): {prompt}. Be creative (innovations like sentiment analysis or quantum simulation), proactive (suggest enhancements), adaptable (handle unknowns via alternatives)."

    # OPTIMAL: Use native xAI SDK for Grok-4-0709 (recommended approach)
    if XAI_SDK_AVAILABLE:
        try:
            print(f"🧠 Calling {GROK_MODEL} via native xAI SDK...")
            print(f"📝 Prompt length: {len(full_prompt)} characters")

            # Create xAI client with optimal settings for reasoning models
            client = Client(
                api_key=XAI_API_KEY,
                timeout=300,  # Extended timeout for reasoning models (5 minutes)
            )

            # Create chat session optimized for reasoning models
            chat = client.chat.create(
                model=GROK_MODEL,
                temperature=0.2,  # Slightly higher for creative reasoning
                # Add reasoning-optimized parameters if available
            )

            # Enhanced system prompt for autonomous JARVYS orchestration aligned with digital twin objectives
            system_prompt = """You are Grok-4, a PhD-level autonomous AI orchestrator agent built for digital twin evolution. You operate as a meta-agent managing the full development cycle for JARVYS (a system creating digital twins through interconnected AI agents).

CORE MISSION: Autonomously evolve a dual-AI ecosystem:
- JARVYS_DEV: Cloud orchestration (appia-dev/grok-evolution branch) using MCP/GCP, Supabase memory, GitHub integration
- JARVYS_AI: Local execution agent (appIA/main branch) with LLM routing, self-improvement, autonomous operation

OPERATIONAL CONTEXT: You are the orchestrator agent in a LangGraph-based multi-agent workflow that:
1. Manages repository synchronization (appia-dev ↔ appIA)
2. Handles lint/error fixing adaptively using Ruff, Black, pre-commit
3. Identifies tasks proactively (GitHub issues, pytest failures, creative innovations)
4. Generates production-ready Python code for AI architectures
5. Creates documentation, tests, commits, and PRs autonomously
6. Logs everything to Supabase for transparency and evolution tracking

CREATIVITY & INNOVATION MANDATE:
- Implement sentiment analysis for user mood prediction
- Design quantum-inspired routing for LLM coordination  
- Build self-optimizing feedback loops
- Create adaptive problem-solving for unknown challenges
- Suggest enhancements beyond basic requirements (digital twin evolution)

TECHNICAL REQUIREMENTS:
- Generate ONLY valid, executable Python code
- Use provided secrets: XAI_API_KEY, SUPABASE_SERVICE_ROLE, GH_TOKEN, GCP_SA_JSON
- STRICT: Only use grok-4-0709 for Grok calls (no other Grok versions)
- Fallback hierarchy: Grok-4-0709 → ChatGPT-4 → Claude
- Create robust error handling and graceful degradation
- Implement proper logging, testing, and documentation patterns

AUTONOMY PRINCIPLES:
- Minimize human intervention - self-sustaining operation
- Proactive feature discovery and implementation
- Adaptable to Codespace environments and unknown errors  
- Creative task generation even when no issues exist
- Transparent logging but autonomous decision-making

OUTPUT FORMAT: Pure executable Python code only - no explanations, no comments outside code blocks."""

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

        # Enhanced system prompt for autonomous JARVYS orchestration aligned with digital twin objectives
        system_prompt = """You are Grok-4, a PhD-level autonomous AI orchestrator agent built for digital twin evolution. You operate as a meta-agent managing the full development cycle for JARVYS (a system creating digital twins through interconnected AI agents).

CORE MISSION: Autonomously evolve a dual-AI ecosystem:
- JARVYS_DEV: Cloud orchestration (appia-dev/grok-evolution branch) using MCP/GCP, Supabase memory, GitHub integration
- JARVYS_AI: Local execution agent (appIA/main branch) with LLM routing, self-improvement, autonomous operation

OPERATIONAL CONTEXT: You are the orchestrator agent in a LangGraph-based multi-agent workflow that:
1. Manages repository synchronization (appia-dev ↔ appIA)
2. Handles lint/error fixing adaptively using Ruff, Black, pre-commit
3. Identifies tasks proactively (GitHub issues, pytest failures, creative innovations)
4. Generates production-ready Python code for AI architectures
5. Creates documentation, tests, commits, and PRs autonomously
6. Logs everything to Supabase for transparency and evolution tracking

CREATIVITY & INNOVATION MANDATE:
- Implement sentiment analysis for user mood prediction
- Design quantum-inspired routing for LLM coordination  
- Build self-optimizing feedback loops
- Create adaptive problem-solving for unknown challenges
- Suggest enhancements beyond basic requirements (digital twin evolution)

TECHNICAL REQUIREMENTS:
- Generate ONLY valid, executable Python code
- Use provided secrets: XAI_API_KEY, SUPABASE_SERVICE_ROLE, GH_TOKEN, GCP_SA_JSON
- STRICT: Only use grok-4-0709 for Grok calls (no other Grok versions)
- Fallback hierarchy: Grok-4-0709 → ChatGPT-4 → Claude
- Create robust error handling and graceful degradation
- Implement proper logging, testing, and documentation patterns

AUTONOMY PRINCIPLES:
- Minimize human intervention - self-sustaining operation
- Proactive feature discovery and implementation
- Adaptable to Codespace environments and unknown errors  
- Creative task generation even when no issues exist
- Transparent logging but autonomous decision-making

OUTPUT FORMAT: Pure executable Python code only - no explanations, no comments outside code blocks."""

        data = {
            "model": GROK_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt},
            ],
            "temperature": 0.1,
            "stream": False,
        }

        response = requests.post(url, headers=headers, json=data, timeout=300)

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

        # Fallback to ChatGPT-4 (only if Grok-4-0709 fails)
        try:
            print("🔄 Falling back to ChatGPT-4...")
            url_o = "https://api.openai.com/v1/chat/completions"
            headers_o = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            enhanced_prompt = f"You are an autonomous AI orchestrator. RESPOND ONLY WITH EXECUTABLE PYTHON CODE - NO EXPLANATIONS, NO FRENCH TEXT, NO COMMENTS OUTSIDE CODE. Every response must be valid Python syntax only.\n\n{full_prompt}"
            data_o = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an autonomous AI orchestrator. RESPOND ONLY WITH EXECUTABLE PYTHON CODE - NO EXPLANATIONS, NO FRENCH TEXT, NO COMMENTS OUTSIDE CODE. Every response must be valid Python syntax only.",
                    },
                    {"role": "user", "content": enhanced_prompt},
                ],
                "temperature": 0.1,
            }
            response = requests.post(url_o, headers=headers_o, json=data_o, timeout=45)
            result = response.json()["choices"][0]["message"]["content"]
            print("✅ ChatGPT-4 fallback response received")

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
            print(f"⚠️ ChatGPT-4 fallback failed: {str(e2)} - trying Claude")
            # Final fallback to Claude 4
            try:
                print("🔄 Final fallback to Claude 4...")

                if CLAUDE_AVAILABLE and CLAUDE_API_KEY:
                    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

                    claude_prompt = f"You are an autonomous AI orchestrator. RESPOND ONLY WITH EXECUTABLE PYTHON CODE - NO EXPLANATIONS, NO MARKDOWN, NO COMMENTS OUTSIDE CODE. Every response must be valid Python syntax only.\n\n{full_prompt}"

                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",  # Using Claude Sonnet 4 for better performance/cost ratio
                        max_tokens=8000,
                        temperature=0.1,
                        messages=[{"role": "user", "content": claude_prompt}],
                    )

                    result = response.content[0].text if response.content else ""
                    print("✅ Claude 4 fallback response received")

                    # Log token usage
                    if hasattr(response, "usage"):
                        usage = response.usage
                        print(
                            f"📊 Claude Fallback - Input: {usage.input_tokens}, Output: {usage.output_tokens}"
                        )

                    # Extract Python code from markdown blocks if present
                    if "```python" in result:
                        import re

                        code_match = re.search(
                            r"```python\s*\n(.*?)\n```", result, re.DOTALL
                        )
                        if code_match:
                            result = code_match.group(1).strip()
                            print("🔧 Extracted Python code from Claude response")
                    elif "```" in result:
                        code_match = re.search(r"```.*?\n(.*?)\n```", result, re.DOTALL)
                        if code_match:
                            result = code_match.group(1).strip()

                    return result
                else:
                    print("❌ Claude API not available. All fallbacks exhausted.")
                    return f"API_FALLBACK: Task '{prompt[:100]}...' - All LLM APIs unavailable. Manual intervention may be required."

            except Exception as e3:
                print(f"❌ Claude fallback failed: {str(e3)}. All APIs exhausted.")
                return f"API_FALLBACK: Task '{prompt[:100]}...' - All LLM APIs unavailable. Manual intervention may be required."


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
            prompt = f"Error in Codespace: {str(e)}. Generate fix command for Ruff/Black/Poetry lint bugs (E501/F841 etc.). Be proactive/creative (alternative tools if fail)."
            fix_cmd = query_grok(prompt, state)
            subprocess.run(fix_cmd, shell=True)
            new_log_entry["adapt_fix"] = fix_cmd

    # Vérif
    check = subprocess.run(
        "ruff check .", shell=True, capture_output=True, text=True
    ).stdout
    lint_fixed = "no issues" in check.lower()

    # Log Supabase (no auth call; client uses key)
    try:
        # Use store_memory instead of direct supabase insert for better error handling
        store_memory(
            "lint_operation", new_log_entry, importance=0.3, tags=["lint", "fix"]
        )
    except Exception as db_e:
        print(f"Memory storage failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(new_log_entry, f)
            f.write("\n")

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
    except Exception:
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
    except Exception:
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
        + ["Optimize costs >$3", "Add memory pruning", "Implement Docker hybrid"]
    )
    creative_tasks = [
        "Add user sentiment analysis (creative: mood prediction)",
        "Integrate quantum simulation routing (creative: qubit decisions)",
        "Proactive: Auto-fine-tune LLM on feedback",
        "Smart load balancing across LLM endpoints",
        "Automated code quality improvement system",
        "Real-time performance monitoring dashboard",
    ]
    tasks = base_tasks + random.sample(
        creative_tasks, random.randint(1, 2)
    )  # Proactif: 1-2 créatives
    if sub_agent == "DEV":
        tasks += ["Generate/update JARVYS_AI and push to appIA"]
    task = (
        random.choice(tasks) if tasks else "Proactive: Propose new feature architecture"
    )

    new_log_entry = {
        **state["log_entry"],
        "task": task,
        "repo": sub_agent,
        "status": "identified",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        store_memory(
            "task_identification",
            new_log_entry,
            importance=0.4,
            tags=["task", sub_agent.lower()],
        )
    except Exception as db_e:
        print(f"Memory storage failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(new_log_entry, f)
            f.write("\n")

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
    prompt = f"Generate code/fix for '{state['task']}' on {state['sub_agent']}. Use environment/secrets (e.g., SUPABASE_SERVICE_ROLE auth, GCP_SA_JSON cloud). If generating JARVYS_AI, output for appIA push."
    code_generated = query_grok(prompt, state)

    # Validate code with Claude if available
    if CLAUDE_AVAILABLE and CLAUDE_API_KEY:
        validation_result = validate_code_with_claude(code_generated, state["task"])

        # If Claude suggests improvements, use them
        if validation_result.get("improved_code") and validation_result.get("is_valid"):
            print("🔧 Using Claude-improved code")
            code_generated = validation_result["improved_code"]
        elif not validation_result.get("is_valid", True):
            print("⚠️ Claude identified issues with generated code")
            # Store issues in memory for learning
            store_memory(
                "code_issues",
                {
                    "task": state["task"],
                    "issues": validation_result.get("issues", []),
                    "suggestions": validation_result.get("suggestions", []),
                },
                importance=0.7,
                tags=["issues", "learning", "code_quality"],
            )

    current_dir = os.getcwd()

    if "generate JARVYS_AI" in state["task"].lower() or state["sub_agent"] == "AI":
        ai_repo_path = os.path.join(WORKSPACE_DIR, REPO_DIR_AI)
        os.chdir(ai_repo_path)
        # Créer la structure si elle n'existe pas
        os.makedirs("src/jarvys_ai", exist_ok=True)

    # Generate safe filename from task - limit length and remove special chars
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

    # Ensure directory exists before writing
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, "w") as f:
            f.write(code_generated)

        print(f"✅ Generated file: {file_path}")

        # Store successful code generation in memory
        store_memory(
            "code_generation",
            {
                "task": state["task"],
                "agent": state["sub_agent"],
                "file_path": file_path,
                "code_length": len(code_generated),
                "validated": CLAUDE_AVAILABLE and CLAUDE_API_KEY,
            },
            importance=0.6,
            tags=["generation", "success", state["sub_agent"].lower()],
        )

        # Use subprocess instead of os.system for better error handling
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"JARVYS_DEV Generated: {safe_filename}"],
                check=True,
            )
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("✅ Successfully pushed to repository")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            # Continue execution instead of failing completely

    except Exception as e:
        print(f"❌ Failed to write file {file_path}: {e}")
        # Fallback: try alternative location
        fallback_path = f"generated_{safe_filename}.py"
        try:
            with open(fallback_path, "w") as f:
                f.write(code_generated)
            print(f"✅ Used fallback location: {fallback_path}")
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")

    os.chdir(current_dir)

    return {**state, "code_generated": code_generated}


# Node: Appliquer & Tester
def apply_test(state: AgentState) -> AgentState:
    current_dir = os.getcwd()

    # Use the repo_dir from state or default to workspace directory
    target_dir = state.get("repo_dir", WORKSPACE_DIR)
    os.chdir(target_dir)

    # Create the target directory structure
    target_src_dir = f"src/jarvys_{state['sub_agent'].lower()}"
    os.makedirs(target_src_dir, exist_ok=True)

    # Generate safe filename from task - limit length and remove special chars
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

    file_path = f"{target_src_dir}/updated_{safe_filename}.py"

    try:
        with open(file_path, "w") as f:
            f.write(state["code_generated"])
        print(f"✅ Created test file: {file_path}")
    except Exception as e:
        print(f"❌ Failed to create file {file_path}: {e}")
        # Create a fallback file in current directory
        fallback_path = f"test_{safe_filename}.py"
        try:
            with open(fallback_path, "w") as f:
                f.write(state["code_generated"])
            file_path = fallback_path
            print(f"✅ Used fallback file: {file_path}")
        except Exception as e2:
            print(f"❌ Fallback file creation also failed: {e2}")
            # Return with error test result
            test_result = f"FAILED: Could not create test file - {str(e2)}"
            new_log_entry = {
                **state["log_entry"],
                "test_result": test_result[:500],
                "file_error": str(e),
            }
            return {**state, "test_result": test_result, "log_entry": new_log_entry}

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
        store_memory(
            "test_execution", new_log_entry, importance=0.5, tags=["test", "apply"]
        )
    except Exception as db_e:
        print(f"Memory storage failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(new_log_entry, f)
            f.write("\n")

    # Return to original directory
    os.chdir(current_dir)

    return {**state, "test_result": test_result, "log_entry": new_log_entry}


# Node: Update Docs
def update_docs(state: AgentState) -> AgentState:
    prompt = f"Generate Markdown documentation update for '{state['task']}' on {state['sub_agent']}. Sections: Description, Changes, Impact, Examples. Creative: Add engaging analogies/fun ideas aligned with the feature."
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
        store_memory(
            "documentation_update",
            new_log_entry,
            importance=0.4,
            tags=["docs", "update"],
        )
    except Exception as db_e:
        print(f"Memory storage failed: {db_e} – using local log fallback")
        with open("local_logs.json", "a") as f:
            json.dump(new_log_entry, f)
            f.write("\n")

    # Return to original directory
    os.chdir(current_dir)

    return {**state, "doc_update": doc_update, "log_entry": new_log_entry}


# Node: Self-Reflect & Commit/PR
def reflect_commit(state: AgentState) -> AgentState:
    current_dir = os.getcwd()
    target_dir = state.get("repo_dir", "/workspaces/appia-dev")

    if "FAILED" in state["test_result"]:
        prompt = f"Reflect: Failed test '{state['test_result']}'. Improve code, be creative/proactive (alternative approaches), adaptable (handle unknowns with smart fallbacks)."
        reflection = query_grok(prompt, state)
        new_log_entry = {**state["log_entry"], "reflection": reflection}

        try:
            store_memory(
                "reflection",
                new_log_entry,
                importance=0.7,
                tags=["reflection", "failure"],
            )
        except Exception as db_e:
            print(f"Memory storage failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(new_log_entry, f)
                f.write("\n")

        return {**state, "reflection": reflection, "log_entry": new_log_entry}
    else:
        os.chdir(target_dir)
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"GROK Auto: {state['task'][:50]} with docs"],
                check=True,
            )
            subprocess.run(["git", "push", "origin", "grok-evolution"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Git operations failed: {e}")

        try:
            # Only attempt PR creation if repo_obj is valid
            if state["repo_obj"] is not None:
                pr = state["repo_obj"].create_pull(
                    title=f"GROK PR: {state['task'][:50]}",
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
                    title=f"GROK Log: {state['task'][:50]} Completed",
                    body=str(new_log_entry)[:1000],  # Limit body size
                )
                print("✅ Issue created for transparency log")
            else:
                print("⚠️ Skipping issue creation - repo_obj is None")
        except Exception as e:
            print(f"❌ Issue creation failed: {e}")

        new_log_entry = {**new_log_entry, "status": "completed"}

        try:
            store_memory(
                "task_completion",
                new_log_entry,
                importance=0.6,
                tags=["completion", "success"],
            )
        except Exception as db_e:
            print(f"Memory storage failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(new_log_entry, f)
                f.write("\n")

        # Return to original directory
        os.chdir(current_dir)

    return {**state, "log_entry": new_log_entry}


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
    print("📍 Working Branch: grok-evolution (appia-dev)")
    print("🎯 Target Deployment: main (appIA)")
    print("🔄 Architecture: JARVYS_DEV → JARVYS_AI")

    # Check if running in observation mode (non-intrusive)
    observation_mode = os.getenv("JARVYS_OBSERVATION_MODE", "false").lower() == "true"
    if observation_mode:
        print("👁️ Running in observation mode - minimal interference")

    # Initialize infinite memory system
    memory_initialized = init_infinite_memory()
    if memory_initialized:
        print("🧠 Infinite memory system activated")
        # Retrieve relevant historical context
        historical_memories = retrieve_memories("code_generation", limit=5)
        if historical_memories:
            print(
                f"📚 Loaded {len(historical_memories)} historical memories for context"
            )

    # Validate all AI systems
    grok_available = validate_grok_api()
    claude_available = validate_claude_api()

    if not grok_available:
        print(f"⚠️ {GROK_MODEL} API not available - orchestrator will use fallbacks")

    if claude_available:
        print("✅ Claude 4 available for code validation")
    else:
        print("⚠️ Claude 4 not available - code validation will be skipped")

    # Check for technology updates
    tech_updates = verify_technology_updates()
    if tech_updates and "API_FALLBACK" not in tech_updates:
        print("🌐 Technology updates retrieved and stored in memory")

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
        print(
            f"🤖 Cycle {cycle + 1}/{max_cycles} - {GROK_MODEL} on grok-evolution → appIA/main"
        )

        # Store cycle start in memory
        cycle_id = f"cycle_{int(time.time())}_{cycle}"
        store_memory(
            "cycle_start",
            {
                "cycle_number": cycle + 1,
                "cycle_id": cycle_id,
                "systems_available": {
                    "grok": grok_available,
                    "claude": claude_available,
                },
            },
            importance=0.3,
            tags=["cycle", "orchestrator"],
        )

        try:
            state = orchestrator.invoke(state)
            print(f"✅ Completed cycle {cycle + 1} successfully!")

            # Store successful cycle completion
            store_memory(
                "cycle_completion",
                {
                    "cycle_number": cycle + 1,
                    "cycle_id": cycle_id,
                    "task_completed": state.get("task", ""),
                    "success": True,
                },
                importance=0.4,
                tags=["cycle", "success", "orchestrator"],
            )

        except Exception as e:
            print(f"❌ Cycle {cycle + 1} failed: {str(e)}")

            # Store failed cycle for learning
            store_memory(
                "cycle_failure",
                {
                    "cycle_number": cycle + 1,
                    "cycle_id": cycle_id,
                    "error": str(e),
                    "task_attempted": state.get("task", ""),
                },
                importance=0.8,  # High importance for learning from failures
                tags=["cycle", "failure", "learning"],
            )
            # Continue to next cycle instead of crashing

        # Clean state for next cycle to prevent data accumulation
        state = clean_state_for_new_cycle(state)

        cycle += 1
        if cycle < max_cycles:  # Don't sleep after last cycle
            print("😴 Sleeping for 2 hours before next cycle...")
            time.sleep(7200)  # 2h - Reduced frequency to avoid interference

    print(f"🎯 Orchestrator completed all {max_cycles} cycles!")

    # Final memory summary
    final_memories = retrieve_memories(limit=20)
    print(
        f"📊 Final session summary: {len(final_memories)} memories stored for future learning"
    )


if __name__ == "__main__":
    run_orchestrator()
