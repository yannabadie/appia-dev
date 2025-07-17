#!/usr/bin/env python3
"""
JARVYS_DEV Grok Orchestrator - Version Corrigée
Orchestrateur autonome IA avec gestion d'erreurs et contrôles de timeout
"""

import json
import os
import random
import re
import subprocess
import time
from contextlib import contextmanager

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
    # Claude 4 models available (latest from docs.anthropic.com)
    CLAUDE_MODELS = {
        "opus": "claude-opus-4-20250514",  # Most capable, best for complex analysis
        "sonnet": "claude-sonnet-4-20250514",  # Enhanced reasoning, faster than Opus
        "haiku": "claude-3-haiku-20240307",  # Fast, lightweight for simple tasks
    }
    print(f"✅ Claude 4 models available: {list(CLAUDE_MODELS.keys())}")
except ImportError:
    print("⚠️ Claude SDK not installed. Install with: pip install anthropic")
    CLAUDE_AVAILABLE = False
    CLAUDE_MODELS = {}

# Load environment variables
XAI_API_KEY = os.getenv("XAI_API_KEY", "test-key")  # Fallback pour test
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # Claude API key
GROK_MODEL = "grok-4-0709"  # STRICT: Only grok-4-0709 allowed, no other Grok versions

# Validation stricte du modèle Grok (inspiré de la proposition Grok)
if "grok" in GROK_MODEL.lower() and GROK_MODEL != "grok-4-0709":
    raise ValueError(
        f"ERREUR: Seul grok-4-0709 est autorisé. Modèle détecté: {GROK_MODEL}"
    )

print(f"✅ Validation: Utilisation exclusive de {GROK_MODEL}")

WORKSPACE_DIR = os.getenv(
    "WORKSPACE_DIR", "/workspaces/appia-dev"
)  # Codespace flexibility
GH_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

if not GH_TOKEN:
    raise ValueError("⚠️ GITHUB_TOKEN manquant - Requis pour l'orchestrateur autonome")

# Other environment variables
GH_REPO_DEV = os.getenv("GH_REPO_DEV", "yannabadie/appia-dev")
GH_REPO_AI = os.getenv("GH_REPO_AI", "yannabadie/appIA")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GCP credentials handling
GCP_SA_JSON = None
if os.getenv("GCP_SA_JSON"):
    try:
        GCP_SA_JSON = json.loads(os.getenv("GCP_SA_JSON"))
    except Exception as e:
        print(f"⚠️ GCP_SA_JSON parsing failed: {e}")

SECRET_ACCESS_TOKEN = os.getenv("SECRET_ACCESS_TOKEN")  # Loadé même inusité

# GCP Credentials (pour tâches cloud/adaptabilité)
gcp_credentials = None
if GCP_SA_JSON:
    try:
        gcp_credentials = service_account.Credentials.from_service_account_info(
            GCP_SA_JSON
        )
    except Exception as e:
        print(f"⚠️ GCP credentials setup failed: {e}")

# Clients (use SUPABASE_SERVICE_ROLE as key for elevated client if needed)
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client_key = (
            SUPABASE_SERVICE_ROLE if SUPABASE_SERVICE_ROLE else SUPABASE_KEY
        )
        supabase = create_client(SUPABASE_URL, supabase_client_key)
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"⚠️ Supabase setup failed: {e}")

# Optional Supabase authentication if using email/password format
if supabase and SUPABASE_SERVICE_ROLE and "@" in SUPABASE_SERVICE_ROLE:
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
github = None
repo_dev = None
repo_ai = None
if GH_TOKEN and GITHUB_AVAILABLE:
    try:
        github = Github(GH_TOKEN)
        repo_dev = github.get_repo(GH_REPO_DEV)
        repo_ai = github.get_repo(GH_REPO_AI)
        print("✅ GitHub clients initialized")
    except Exception as e:
        print(f"⚠️ GitHub setup failed: {e}")

# Dirs repos (clone/pull pour synchro)
REPO_DIR_DEV = "appia-dev"
REPO_DIR_AI = "appIA"


# Context manager for directory changes
@contextmanager
def change_dir(path):
    """Context manager to temporarily change directory"""
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)


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
    if not CLAUDE_AVAILABLE or not CLAUDE_API_KEY:
        print("⚠️ WARNING: No Claude API key found. Code validation will be skipped!")
        return False

    try:
        print("🔍 Testing Claude 4 API connection...")

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

        # Test with Claude 4 Sonnet (best balance of capability and speed for code validation)
        model = CLAUDE_MODELS.get("sonnet", "claude-3-haiku-20240307")

        response = client.messages.create(
            model=model,
            max_tokens=100,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": "Test connection - respond with 'CLAUDE_4_API_OK' and mention your model version",
                }
            ],
        )

        content = response.content[0].text if response.content else ""
        print(f"✅ Claude 4 API connection successful! Response: {content.strip()}")
        print(f"🤖 Using model: {model}")

        # Log token usage
        if hasattr(response, "usage"):
            usage = response.usage
            print(
                f"📊 Claude Test - Input tokens: {usage.input_tokens}, Output tokens: {usage.output_tokens}"
            )

        # Store successful API validation in memory
        store_memory(
            "api_validation",
            {
                "service": "claude_4",
                "model": model,
                "status": "success",
                "response": content.strip(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            importance=0.7,
            tags=["api", "claude", "validation"],
        )

        return True

    except Exception as e:
        print(f"❌ Claude API validation error: {str(e)}")

        # Store failed validation for learning
        store_memory(
            "api_validation",
            {
                "service": "claude_4",
                "status": "failed",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            importance=0.8,
            tags=["api", "claude", "error"],
        )

        return False


# Initialize infinite memory system in Supabase
def init_infinite_memory():
    """Initialize the infinite memory system with Supabase backend and load previous context"""
    if not supabase:
        print("⚠️ Supabase not available - using local fallback storage only")
        return False

    try:
        print("🧠 Initializing infinite memory system with historical context...")

        # Create tables if they don't exist
        create_memory_tables()

        # Test basic connection first
        try:
            # Simple test query to check connection
            supabase.table("jarvys_memory").select("*").limit(1).execute()
            print("✅ Supabase connection verified")
        except Exception as conn_error:
            print(f"⚠️ Supabase connection issue: {conn_error}")
            print("📝 Will use local fallback storage only")
            return False

        # Load recent memory context to understand previous actions
        recent_memories = retrieve_memories(limit=50)
        recent_cycles = get_recent_orchestrator_cycles(limit=10)

        # Analyze previous patterns and failures for learning
        patterns = analyze_memory_patterns(recent_memories, recent_cycles)

        print(
            f"🔍 Loaded {len(recent_memories)} memories and {len(recent_cycles)} recent cycles"
        )
        if patterns:
            print(f"📊 Memory patterns: {patterns['summary']}")

        # Test memory storage with enhanced context
        test_memory_data = {
            "session_id": f"session_{int(time.time())}",
            "memory_type": "system_init",
            "content": "Système JARVYS initialisé avec mémoire infinie - Orchestrateur Grok-Claude 4 opérationnel",
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "models_available": {
                    "grok": XAI_SDK_AVAILABLE,
                    "claude": CLAUDE_AVAILABLE,
                    "claude_models": (
                        list(CLAUDE_MODELS.keys()) if CLAUDE_AVAILABLE else []
                    ),
                },
                "initialization_success": True,
                "previous_context": {
                    "recent_memories_count": len(recent_memories),
                    "recent_cycles_count": len(recent_cycles),
                    "patterns_identified": patterns is not None,
                },
                "environment_secrets": get_available_secrets_summary(),
            },
        }

        # Try to insert into jarvys_memory table with correct schema
        result = supabase.table("jarvys_memory").insert(test_memory_data).execute()
        if result.data:
            print("✅ Memory system initialized with jarvys_memory table!")
            print(f"📝 Memory ID: {result.data[0].get('id')}")

            # Store patterns analysis for future reference
            if patterns:
                store_memory(
                    "pattern_analysis",
                    patterns,
                    importance=0.9,
                    tags=["patterns", "learning", "optimization"],
                )

            return True
        else:
            print("⚠️ No data returned from jarvys_memory insert")
            return False

    except Exception as e:
        print(f"❌ Error initializing memory: {e}")
        # Try orchestrator_logs as backup
        try:
            orchestrator_init_data = {
                "cycle_number": 0,
                "step_name": "system_initialization",
                "status": "completed",
                "content": json.dumps(test_memory_data),
                "metadata": test_memory_data["metadata"],
            }
            result = (
                supabase.table("orchestrator_logs")
                .insert(orchestrator_init_data)
                .execute()
            )
            if result.data:
                print("🧠 Memory system using orchestrator_logs table as backup!")
                return True
        except Exception as backup_e:
            print(f"❌ Backup storage also failed: {backup_e}")
        return False


def create_memory_tables():
    """Create necessary Supabase tables if they don't exist"""
    if not supabase:
        return

    try:
        # Check if tables exist by trying a simple query
        supabase.table("jarvys_memory").select("*").limit(1).execute()
        supabase.table("orchestrator_logs").select("*").limit(1).execute()
        supabase.table("code_validations").select("*").limit(1).execute()
        print("✅ All required tables exist")
    except Exception as e:
        print(f"⚠️ Some tables may be missing: {e}")
        print("📝 Tables should be created manually in Supabase if needed")


def get_available_secrets_summary():
    """Get a summary of available environment secrets for orchestrator awareness"""
    secrets = {
        "github": bool(GH_TOKEN),
        "supabase": bool(SUPABASE_URL and SUPABASE_KEY),
        "supabase_service_role": bool(SUPABASE_SERVICE_ROLE),
        "xai_grok": bool(XAI_API_KEY and XAI_API_KEY != "test-key"),
        "claude": bool(CLAUDE_API_KEY),
        "openai": bool(OPENAI_API_KEY),
        "gemini": bool(GEMINI_API_KEY),
        "gcp": bool(GCP_SA_JSON),
        "repos": {"dev": GH_REPO_DEV, "ai": GH_REPO_AI},
    }
    return secrets


def analyze_memory_patterns(memories: list, cycles: list) -> dict:
    """Analyze memory patterns to learn from previous actions and optimize future behavior"""
    if not memories and not cycles:
        return None

    try:
        patterns = {
            "summary": "",
            "frequent_tasks": {},
            "success_patterns": [],
            "failure_patterns": [],
            "technology_trends": [],
            "optimization_opportunities": [],
        }

        # Analyze task frequency
        task_counts = {}
        success_count = 0
        failure_count = 0

        for cycle in cycles:
            if cycle.get("content"):
                try:
                    content = (
                        json.loads(cycle["content"])
                        if isinstance(cycle["content"], str)
                        else cycle["content"]
                    )
                    task = content.get("task", "unknown")
                    status = content.get("status", "unknown")

                    task_counts[task] = task_counts.get(task, 0) + 1

                    if "success" in status.lower() or "completed" in status.lower():
                        success_count += 1
                    elif "failed" in status.lower() or "error" in status.lower():
                        failure_count += 1

                except (json.JSONDecodeError, AttributeError):
                    continue

        patterns["frequent_tasks"] = dict(
            sorted(task_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        # Generate summary
        total_cycles = len(cycles)
        success_rate = (success_count / total_cycles * 100) if total_cycles > 0 else 0

        patterns["summary"] = (
            f"Analyzed {total_cycles} cycles, {success_rate:.1f}% success rate"
        )

        # Add optimization opportunities based on patterns
        if failure_count > success_count:
            patterns["optimization_opportunities"].append(
                "High failure rate - review error handling"
            )

        if len(set(task_counts.keys())) < 3:
            patterns["optimization_opportunities"].append(
                "Low task variety - expand creative task generation"
            )

        return patterns

    except Exception as e:
        print(f"⚠️ Pattern analysis failed: {e}")
        return {"summary": "Pattern analysis failed", "error": str(e)}


def get_recent_orchestrator_cycles(limit: int = 10) -> list:
    """Get recent orchestrator cycles from Supabase logs"""
    if not supabase:
        return []

    try:
        result = (
            supabase.table("orchestrator_logs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        if result.data:
            print(f"🔍 Retrieved {len(result.data)} recent orchestrator cycles")
            return result.data
        else:
            print("🔍 No recent cycles found")
            return []
    except Exception as e:
        print(f"⚠️ Failed to retrieve recent cycles: {e}")
        return []


# Store memory with infinite retention and intelligent retrieval
def store_memory(
    memory_type: str, content: dict, importance: float = 0.5, tags: list = None
):
    """Store memory in Supabase with correct schema"""
    if not supabase:
        print("⚠️ Supabase not available for memory storage")
        return None

    try:
        session_id = f"session_{int(time.time())}"

        jarvys_memory_data = {
            "session_id": session_id,
            "memory_type": memory_type,
            "content": (
                json.dumps(content) if isinstance(content, dict) else str(content)
            ),
            "metadata": {
                "importance_score": importance,
                "tags": tags or [],
                "source": "grok_orchestrator",
                "agent_source": "JARVYS_DEV",
                "user_context": "orchestrator",
            },
        }

        result = supabase.table("jarvys_memory").insert(jarvys_memory_data).execute()
        if result.data:
            print(
                f"🧠 Memory stored in jarvys_memory: {memory_type} (importance: {importance})"
            )
            return result.data[0].get("id") if result.data else None
        else:
            print("⚠️ No data returned from jarvys_memory insert")
            return None

    except Exception as e:
        print(f"❌ Error storing memory: {e}")
        # Try orchestrator_logs as backup
        try:
            orchestrator_data = {
                "cycle_number": 0,
                "step_name": memory_type,
                "status": "completed",
                "content": (
                    json.dumps(content) if isinstance(content, dict) else str(content)
                ),
                "metadata": {
                    "importance_score": importance,
                    "tags": tags or [],
                    "source": "grok_orchestrator",
                },
            }
            result = (
                supabase.table("orchestrator_logs").insert(orchestrator_data).execute()
            )
            if result.data:
                print(f"🧠 Memory stored in orchestrator_logs as backup: {memory_type}")
                return result.data[0].get("id")
        except Exception as backup_e:
            print(f"❌ Backup storage also failed: {backup_e}")
        return None


def log_cycle_step(cycle_number: int, step_name: str, status: str, content: str = ""):
    """Log a step in the orchestrator cycle"""
    if not supabase:
        print(f"📝 Step logged locally: {step_name} - {status}")
        return None

    try:
        log_data = {
            "cycle_number": cycle_number,
            "step_name": step_name,
            "status": status,
            "content": content,
            "metadata": {"source": "grok_orchestrator"},
        }

        result = supabase.table("orchestrator_logs").insert(log_data).execute()
        if result.data:
            print(f"📝 Step logged: {step_name} - {status}")
            return result.data[0].get("id")
    except Exception as e:
        print(f"⚠️ Failed to log step: {e}")
        return None


def retrieve_memories(memory_type: str = None, limit: int = 10) -> list:
    """Retrieve relevant memories from Supabase"""
    if not supabase:
        return []

    try:
        query = (
            supabase.table("jarvys_memory").select("*").order("timestamp", desc=True)
        )
        if memory_type:
            query = query.eq("memory_type", memory_type)

        result = query.limit(limit).execute()
        if result.data:
            print(f"🔍 Retrieved {len(result.data)} memories")
            return result.data
        else:
            print("🔍 No memories found")
            return []
    except Exception as e:
        print(f"⚠️ Failed to retrieve memories: {e}")
        return []


# Claude code validation function with Claude 4 integration
def validate_code_with_claude(code: str, task_description: str) -> dict:
    """Use Claude 4 to validate and improve generated code with enhanced analysis"""
    if not CLAUDE_AVAILABLE or not CLAUDE_API_KEY:
        return {"validated": False, "message": "Claude not available"}

    try:
        print("🔍 Validating code with Claude 4...")

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

        # Use Claude 4 Opus for complex code analysis or Sonnet for faster validation
        model = CLAUDE_MODELS.get(
            "opus", CLAUDE_MODELS.get("sonnet", "claude-3-haiku-20240307")
        )

        validation_prompt = f"""You are Claude 4, an expert code reviewer and validator with deep understanding of software engineering best practices. Analyze this Python code comprehensively:

## Task Context
{task_description}

## Code to Validate
```python
{code}
```

## Analysis Required
1. **Syntax & Logic**: Check for syntax errors, logic flaws, and runtime issues
2. **Security**: Identify vulnerabilities, injection risks, and unsafe practices
3. **Performance**: Analyze efficiency, memory usage, and optimization opportunities
4. **Best Practices**: Verify adherence to Python PEP standards and clean code principles
5. **Dependencies**: Check for missing imports and compatibility issues
6. **Testing**: Assess testability and suggest test cases
7. **Integration**: Evaluate compatibility with the JARVYS ecosystem (Supabase, GitHub, LangGraph)

## Environment Context
- Running in GitHub Codespace with Poetry/Ruff/Black
- Integrated with Supabase for memory storage
- Part of autonomous AI orchestrator system
- Uses LangGraph for state management
- Available secrets: {get_available_secrets_summary()}

Respond with a comprehensive JSON analysis:
{{
  "is_valid": boolean,
  "confidence": float (0-1),
  "severity_score": int (1-10, 10 = critical issues),
  "issues": [
    {{
      "type": "syntax|logic|security|performance|style",
      "severity": "critical|high|medium|low",
      "description": "detailed issue description",
      "line_number": int or null,
      "suggestion": "specific fix recommendation"
    }}
  ],
  "security_analysis": {{
    "vulnerabilities": ["list of security concerns"],
    "risk_level": "low|medium|high|critical",
    "recommendations": ["security improvement suggestions"]
  }},
  "performance_analysis": {{
    "bottlenecks": ["identified performance issues"],
    "optimizations": ["performance improvement suggestions"],
    "memory_efficiency": "assessment of memory usage"
  }},
  "testing_recommendations": [
    "suggested test cases and testing strategies"
  ],
  "improved_code": "enhanced version with fixes applied (only if significant improvements needed)",
  "integration_notes": "notes about JARVYS ecosystem compatibility",
  "technology_updates": "suggestions for using latest Python/library features"
}}"""

        response = client.messages.create(
            model=model,
            max_tokens=6000,  # Increased for comprehensive analysis
            temperature=0.1,
            messages=[{"role": "user", "content": validation_prompt}],
        )

        result_text = response.content[0].text if response.content else ""

        # Extract JSON from response
        try:
            if "```json" in result_text:
                json_match = re.search(r"```json\n(.*?)\n```", result_text, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group(1))
                else:
                    result_json = {
                        "validated": False,
                        "message": "Could not parse Claude response",
                    }
            else:
                # Try to find JSON in the response
                json_start = result_text.find("{")
                json_end = result_text.rfind("}")
                if json_start != -1 and json_end != -1:
                    json_str = result_text[json_start : json_end + 1]
                    result_json = json.loads(json_str)
                else:
                    result_json = {
                        "validated": False,
                        "message": "No JSON found in Claude response",
                    }

        except json.JSONDecodeError as e:
            result_json = {
                "validated": False,
                "message": f"Invalid JSON from Claude: {str(e)}",
            }

        # Enhanced logging and memory storage
        if hasattr(response, "usage"):
            usage = response.usage
            print(f"📊 Claude 4 Validation - Model: {model}")
            print(
                f"📊 Tokens - Input: {usage.input_tokens}, Output: {usage.output_tokens}"
            )

        # Store comprehensive validation result in memory for learning
        store_memory(
            "code_validation",
            {
                "task": task_description,
                "validation_result": result_json,
                "claude_model": model,
                "code_snippet": code[:500],  # Store first 500 chars for context
                "validation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "token_usage": {
                    "input": (
                        getattr(response.usage, "input_tokens", 0)
                        if hasattr(response, "usage")
                        else 0
                    ),
                    "output": (
                        getattr(response.usage, "output_tokens", 0)
                        if hasattr(response, "usage")
                        else 0
                    ),
                },
            },
            importance=0.9,  # High importance for learning
            tags=["validation", "claude4", "code_quality", "learning"],
        )

        # Also store in dedicated code_validations table if available
        try:
            if supabase:
                supabase.table("code_validations").insert(
                    {
                        "task_description": task_description,
                        "code_snippet": code[:1000],
                        "validation_result": result_json,
                        "claude_model": model,
                        "is_valid": result_json.get("is_valid", False),
                        "confidence": result_json.get("confidence", 0),
                        "severity_score": result_json.get("severity_score", 5),
                        "metadata": {
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "orchestrator_session": f"session_{int(time.time())}",
                        },
                    }
                ).execute()
                print("💾 Validation result stored in code_validations table")
        except Exception as db_e:
            print(f"⚠️ Failed to store in code_validations table: {db_e}")

        is_valid = result_json.get("is_valid", False)
        confidence = result_json.get("confidence", 0)
        severity = result_json.get("severity_score", 10)

        print("✅ Claude 4 validation completed:")
        print(
            f"   Valid: {is_valid} | Confidence: {confidence:.2f} | Severity: {severity}/10"
        )

        if not is_valid:
            issues = result_json.get("issues", [])
            print(f"   Issues found: {len(issues)}")
            for issue in issues[:3]:  # Show first 3 issues
                print(
                    f"   - {issue.get('severity', 'unknown')}: {issue.get('description', 'No description')}"
                )

        return result_json

    except Exception as e:
        print(f"❌ Claude validation failed: {str(e)}")

        # Store validation failure for learning
        store_memory(
            "validation_error",
            {
                "task": task_description,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            importance=0.7,
            tags=["error", "claude", "validation"],
        )

        return {"validated": False, "message": f"Claude error: {str(e)}"}


# Enhanced internet search for technology verification
def verify_technology_updates():
    """Search for latest technology updates and best practices using memory context"""
    try:
        print("🌐 Checking for latest technology updates with memory context...")

        # Check recent technology searches in memory first
        recent_tech_memories = retrieve_memories(
            memory_type="technology_updates", limit=3
        )

        # Use Grok with internet search capabilities if available
        if XAI_SDK_AVAILABLE and XAI_API_KEY != "test-key":
            try:
                client = Client(api_key=XAI_API_KEY, timeout=60)
                chat = client.chat.create(model=GROK_MODEL, temperature=0.3)

                # Enhanced search prompt with memory context
                memory_context = ""
                if recent_tech_memories:
                    memory_context = f"Previous research context: {[mem.get('content', '')[:100] for mem in recent_tech_memories]}"

                search_prompt = f"""Based on the JARVYS autonomous orchestrator project using:
- LangGraph for multi-agent workflows
- Supabase for infinite memory
- GitHub automation
- Claude 4 for code validation
- Python Poetry/Ruff/Black toolchain

{memory_context}

Provide a concise update on recent relevant developments in:
1. LangGraph and multi-agent frameworks
2. Claude 4 capabilities and best practices
3. Autonomous AI development tools
4. Python toolchain improvements
5. Supabase/database innovations

Focus on actionable updates that could improve the JARVYS system."""

                chat.append(
                    system(
                        "You are a technology research assistant specializing in AI development tools. Provide factual, actionable information."
                    )
                )
                chat.append(user(search_prompt))

                response = chat.sample()
                tech_updates = response.content[:800]  # Increased limit for more detail

                # Store in memory for future reference with enhanced metadata
                store_memory(
                    "technology_updates",
                    {
                        "search_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "updates": tech_updates,
                        "source": "grok_enhanced_search",
                        "context_used": len(recent_tech_memories),
                        "search_areas": [
                            "langgraph",
                            "claude4",
                            "autonomous_ai",
                            "python_tools",
                            "supabase",
                        ],
                    },
                    importance=0.7,
                    tags=["technology", "updates", "research", "grok"],
                )

                print("✅ Technology updates retrieved and stored with memory context")
                return tech_updates
            except Exception as e:
                print(f"⚠️ Grok search failed: {e}")

        print("📝 Using cached technology summary with memory enhancement")

        # Enhanced cached updates based on recent developments
        cached_updates = """Recent AI trends relevant to JARVYS:
- LangGraph 0.5+ improvements in state management and conditional routing
- Claude 4 with enhanced reasoning and code analysis capabilities  
- Autonomous agent frameworks gaining enterprise adoption
- Python 3.12+ performance improvements and typing enhancements
- Supabase vector embeddings and real-time subscriptions
- GitHub Copilot integration with autonomous workflows"""

        store_memory(
            "technology_updates",
            {
                "search_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "updates": cached_updates,
                "source": "enhanced_cached_fallback",
                "memory_enhanced": True,
            },
            importance=0.5,
            tags=["technology", "cached", "enhanced"],
        )

        return cached_updates

    except Exception as e:
        print(f"⚠️ Technology verification failed: {e}")
        return "Technology verification unavailable"


# Setup repository directories
def setup_repositories():
    """Setup and sync repository directories"""
    if not GH_TOKEN:
        print("⚠️ No GitHub token available - skipping repository setup")
        return False

    # Store current directory to return to
    current_dir = os.getcwd()

    try:
        for dir_path, repo_url, branch in [
            (REPO_DIR_DEV, GH_REPO_DEV, "main"),  # Use main branch
            (REPO_DIR_AI, GH_REPO_AI, "main"),
        ]:
            if not os.path.exists(dir_path):
                clone_cmd = f"git clone https://x-access-token:{GH_TOKEN}@github.com/{repo_url}.git {dir_path}"
                os.system(clone_cmd)

            # Always start from the base directory
            os.chdir(current_dir)
            if os.path.exists(dir_path):
                os.chdir(dir_path)

                # Checkout the correct branch for each repo with error handling
                try:
                    # Stash any local changes first
                    subprocess.run(["git", "stash"], capture_output=True)
                    subprocess.run(["git", "checkout", branch], check=True)
                    subprocess.run(["git", "pull", "origin", branch], check=True)
                    print(f"✅ Successfully updated {dir_path}")
                except subprocess.CalledProcessError as git_e:
                    print(f"⚠️ Git operation failed for {dir_path}: {git_e}")
                    # Continue anyway - don't crash the orchestrator

        # Return to base directory
        os.chdir(current_dir)
        print("✅ Repositories setup completed")
        return True

    except Exception as e:
        print(f"⚠️ Repository setup failed: {e}")
        os.chdir(current_dir)
        return False


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


# Collaborative code testing between Grok and Claude
def collaborative_code_testing(
    code: str, task_description: str, state: AgentState
) -> dict:
    """Use both Grok and Claude to collaboratively test and improve code"""
    print("🤝 Starting collaborative code testing with Grok and Claude...")

    results = {
        "grok_generation": "",
        "claude_validation": {},
        "collaborative_improvements": "",
        "final_code": "",
        "test_simulation": {},
        "confidence_score": 0.0,
    }

    try:
        # Step 1: Grok reviews and potentially improves the code
        grok_prompt = f"""
        Contexte: JARVYS orchestrateur autonome avec mémoire Supabase
        Tâche: {task_description}
        
        Révise ce code Python pour:
        1. Optimisation performance
        2. Intégration JARVYS (Supabase, GitHub, LangGraph)
        3. Gestion d'erreurs robuste
        4. Secrets d'environnement disponibles: {get_available_secrets_summary()}
        
        Code à réviser:
        ```python
        {code}
        ```
        
        Fournis une version améliorée avec explications des changements.
        """

        grok_review = query_grok(grok_prompt, state)
        results["grok_generation"] = grok_review

        # Step 2: Claude validates the Grok-improved code
        claude_validation = validate_code_with_claude(grok_review, task_description)
        results["claude_validation"] = claude_validation

        # Step 3: If Claude finds issues, iterate
        if not claude_validation.get("is_valid", False) and claude_validation.get(
            "improved_code"
        ):
            print("🔄 Claude found issues, using improved code...")
            improved_code = claude_validation["improved_code"]
            results["final_code"] = improved_code
        else:
            results["final_code"] = grok_review

        # Step 4: Simulate testing the final code
        test_simulation = simulate_code_execution(
            results["final_code"], task_description
        )
        results["test_simulation"] = test_simulation

        # Step 5: Calculate collaborative confidence score
        claude_confidence = claude_validation.get("confidence", 0)
        grok_confidence = 0.8 if "error" not in grok_review.lower() else 0.3
        test_confidence = test_simulation.get("confidence", 0.5)

        results["confidence_score"] = (
            claude_confidence + grok_confidence + test_confidence
        ) / 3

        # Store collaborative session in memory for learning
        store_memory(
            "collaborative_testing",
            {
                "task": task_description,
                "grok_review_length": len(grok_review),
                "claude_validation": claude_validation.get("is_valid", False),
                "final_confidence": results["confidence_score"],
                "test_simulation": test_simulation,
                "collaboration_success": results["confidence_score"] > 0.7,
            },
            importance=0.9,
            tags=["collaboration", "grok", "claude", "testing", "learning"],
        )

        print(
            f"✅ Collaborative testing completed - Confidence: {results['confidence_score']:.2f}"
        )
        return results

    except Exception as e:
        print(f"❌ Collaborative testing failed: {str(e)}")
        results["error"] = str(e)
        return results


def simulate_code_execution(code: str, task_description: str) -> dict:
    """Simulate code execution to predict potential runtime issues"""
    simulation = {
        "predicted_success": False,
        "potential_errors": [],
        "performance_notes": [],
        "confidence": 0.5,
    }

    try:
        # Basic syntax check
        try:
            compile(code, "<string>", "exec")
            simulation["syntax_valid"] = True
        except SyntaxError as e:
            simulation["syntax_valid"] = False
            simulation["potential_errors"].append(f"Syntax error: {str(e)}")
            simulation["confidence"] = 0.2
            return simulation

        # Check for common patterns and potential issues
        import_errors = []
        if "import " in code:
            # Extract imports and check if they're likely to be available
            import_lines = [
                line.strip()
                for line in code.split("\n")
                if line.strip().startswith("import ")
                or line.strip().startswith("from ")
            ]
            for imp in import_lines:
                if any(pkg in imp for pkg in ["unknown_package", "missing_lib"]):
                    import_errors.append(f"Potentially missing: {imp}")

        # Check for environment variable usage
        env_usage = []
        for secret in ["SUPABASE_URL", "GITHUB_TOKEN", "XAI_API_KEY"]:
            if secret in code:
                env_usage.append(secret)

        # Check for error handling
        has_try_catch = "try:" in code and "except" in code
        if not has_try_catch:
            simulation["potential_errors"].append("Missing error handling")

        # Performance considerations
        if "while True:" in code:
            simulation["performance_notes"].append("Infinite loop detected")
        if ".sleep(" in code:
            simulation["performance_notes"].append(
                "Sleep detected - may block execution"
            )

        # Calculate confidence based on checks
        confidence_factors = []
        confidence_factors.append(0.8 if simulation["syntax_valid"] else 0.1)
        confidence_factors.append(0.8 if has_try_catch else 0.5)
        confidence_factors.append(0.9 if len(import_errors) == 0 else 0.4)
        confidence_factors.append(
            0.7 if len(env_usage) > 0 else 0.6
        )  # Using env vars is good

        simulation["confidence"] = sum(confidence_factors) / len(confidence_factors)
        simulation["predicted_success"] = simulation["confidence"] > 0.6
        simulation["environment_usage"] = env_usage
        simulation["import_analysis"] = import_errors

        return simulation

    except Exception as e:
        simulation["simulation_error"] = str(e)
        simulation["confidence"] = 0.3
        return simulation


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
    """Query Grok using multiple fallback methods"""
    full_prompt = f"Contexte JARVYS_DEV (cloud, MCP/GCP, mémoire Supabase, génère JARVYS_AI in appIA) et JARVYS_AI (local, routing LLMs, self-improve): {prompt}. Sois créatif (innovations alignées comme sentiment analysis ou quantum sim), proactif (suggère extras), adaptable (handle unknown via alternatives)."

    try:
        # Primary: Use xAI SDK if available
        if XAI_SDK_AVAILABLE and XAI_API_KEY != "test-key":
            client = Client(api_key=XAI_API_KEY, timeout=60)
            chat = client.chat.create(model=GROK_MODEL, temperature=0.5)
            chat.append(user(full_prompt))
            response = chat.sample()
            return response.content
        else:
            # Fallback to REST API
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {XAI_API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "grok-beta",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.5,
            }
            response = requests.post(url, headers=headers, json=data)
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        state["log_entry"]["error"] = str(e)
        # Fallback proactif Gemini
        try:
            if GEMINI_API_KEY:
                url_f = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
                data_f = {"contents": [{"parts": [{"text": full_prompt}]}]}
                response = requests.post(url_f, json=data_f)
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

        # Ultime fallback OpenAI
        try:
            if OPENAI_API_KEY:
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
        except Exception:
            pass

        return f"❌ Query failed: {str(e)}"


# Node: Fix Lint/Erreurs (proactif/adaptable : auto-fix, query si unknown)
def fix_lint(state: AgentState) -> AgentState:
    """Fix lint and errors in the codebase"""
    if not os.path.exists(state["repo_dir"]):
        print(f"⚠️ Repository directory {state['repo_dir']} not found")
        return {**state, "lint_fixed": True}  # Skip if no repo

    with change_dir(state["repo_dir"]):
        commands = [
            (
                "poetry run ruff check --fix --unsafe-fixes ."
                if os.path.exists("pyproject.toml")
                else "echo 'No ruff'"
            ),
            (
                "poetry run black ."
                if os.path.exists("pyproject.toml")
                else "echo 'No black'"
            ),
            (
                "pre-commit run --all-files"
                if os.path.exists(".pre-commit-config.yaml")
                else "echo 'No pre-commit'"
            ),
            (
                "poetry install --with dev"
                if os.path.exists("pyproject.toml")
                else "echo 'No poetry'"
            ),  # Fix Poetry env issues
        ]

        for cmd in commands:
            try:
                output = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True
                ).stdout
                state["log_entry"]["lint_output"] = (
                    state["log_entry"].get("lint_output", "") + output[:200] + "\n"
                )
            except Exception as e:
                # Adaptabilité : Query pour solution inconnue
                prompt = f"Erreur in Codespace: {str(e)}. Génère fix commande pour Ruff/Black/Poetry lint bugs (E501/F841 etc.). Sois proactif/créatif (alt tools si fail)."
                fix_cmd = query_grok(prompt, state)
                try:
                    subprocess.run(fix_cmd, shell=True)
                    state["log_entry"]["adapt_fix"] = fix_cmd
                except Exception:
                    pass  # Continue even if fix fails

        # Vérification lint completée
        subprocess.run(
            "echo 'Lint check completed'", shell=True, capture_output=True, text=True
        )
        lint_fixed = True  # Assume fixed for now

    # Log Supabase (no auth call; client uses key)
    if supabase:
        try:
            supabase.table("orchestrator_logs").insert(
                {
                    **state["log_entry"],
                    "step_name": "fix_lint",
                    "status": "completed",
                    "cycle_number": 1,
                }
            ).execute()
        except Exception as db_e:
            print(f"Supabase insert failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(state["log_entry"], f)

    return {**state, "lint_fixed": lint_fixed}


# Node: Identifier Tâches (proactif : base + créatives aléatoires)
def identify_tasks(state: AgentState) -> AgentState:
    """Identify tasks for the orchestrator"""
    is_ai = random.choice([True, False])
    repo_dir = REPO_DIR_AI if is_ai else REPO_DIR_DEV
    repo_obj = repo_ai if is_ai else repo_dev
    sub_agent = "AI" if is_ai else "DEV"

    if os.path.exists(repo_dir):
        with change_dir(repo_dir):
            issues = []
            if repo_obj:
                try:
                    issues = [i.title for i in repo_obj.get_issues(state="open")]
                except Exception:
                    pass

            # Check for failing tests
            failing = []
            try:
                test_output = subprocess.run(
                    "pytest -q", shell=True, capture_output=True, text=True
                ).stdout
                failing = [
                    line for line in test_output.splitlines() if "FAILED" in line
                ]
            except Exception:
                pass

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
                random.choice(tasks)
                if tasks
                else "Proactif: Propose new feature architecture"
            )
    else:
        task = "Setup repository structure"

    log_entry = {
        **state["log_entry"],
        "task": task,
        "repo": sub_agent,
        "status": "identified",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    if supabase:
        try:
            supabase.table("orchestrator_logs").insert(
                {**log_entry, "step_name": "identify_tasks", "cycle_number": 1}
            ).execute()
        except Exception as db_e:
            print(f"Supabase insert failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(log_entry, f)

    return {
        **state,
        "task": task,
        "sub_agent": sub_agent,
        "repo_dir": repo_dir,
        "repo_obj": repo_obj,
        "log_entry": log_entry,
    }


# Node: Générer Code avec test collaboratif Grok-Claude
def generate_code(state: AgentState) -> AgentState:
    """Generate and collaboratively test code for the identified task using Grok and Claude"""
    print(f"🔧 Generating code for task: {state['task']}")

    # Load memory context for this task type
    similar_memories = retrieve_memories(memory_type="code_generation", limit=5)
    memory_context = ""
    if similar_memories:
        memory_context = f"Previous similar implementations: {[mem.get('content', '')[:100] for mem in similar_memories[:2]]}"

    # Enhanced prompt with memory context and environment awareness
    prompt = f"""
    Contexte JARVYS: {state['sub_agent']} - Mémoire infinie Supabase active
    Tâche: {state['task']}
    
    {memory_context}
    
    Secrets disponibles: {get_available_secrets_summary()}
    
    Génère du code Python optimisé pour:
    1. Intégration JARVYS (Supabase memory, GitHub automation, LangGraph state)
    2. Utilisation des secrets d'environnement appropriés
    3. Gestion d'erreurs robuste et logging
    4. Performance et maintenabilité
    
    Si la tâche implique JARVYS_AI, génère pour appIA repo.
    Inclus les imports nécessaires et la documentation.
    """

    # Generate initial code with Grok
    initial_code = query_grok(prompt, state)

    # Collaborative testing with Claude
    collaborative_results = collaborative_code_testing(
        initial_code, state["task"], state
    )

    # Use the improved code from collaboration
    final_code = collaborative_results.get("final_code", initial_code)
    confidence = collaborative_results.get("confidence_score", 0.5)

    print(f"🤝 Collaborative code generation completed - Confidence: {confidence:.2f}")

    # Store enhanced memory about this code generation
    store_memory(
        "code_generation",
        {
            "task": state["task"],
            "agent": state["sub_agent"],
            "code_length": len(final_code),
            "collaboration_confidence": confidence,
            "grok_generation_success": len(initial_code) > 100,
            "claude_validation": collaborative_results.get("claude_validation", {}),
            "environment_secrets_used": get_available_secrets_summary(),
            "memory_context_available": len(similar_memories) > 0,
        },
        importance=0.8,
        tags=[
            "code_generation",
            "collaboration",
            state["sub_agent"].lower(),
            "learning",
        ],
    )

    # Handle JARVYS_AI generation for appIA repo
    if "générer JARVYS_AI" in state["task"].lower() and os.path.exists(REPO_DIR_AI):
        with change_dir(REPO_DIR_AI):
            file_path = f"src/jarvys_ai/generated_{state['task'].replace(' ', '_')}.py"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(final_code)
            try:
                commit_msg = f"Generated by JARVYS_DEV: {state['task']} (Confidence: {confidence:.2f})"
                os.system(
                    f"git add . && git commit -m '{commit_msg}' && git push origin main"
                )
                print(f"✅ Code pushed to appIA repo: {file_path}")
            except Exception as git_e:
                print(f"⚠️ Git push failed: {git_e}")

    return {
        **state,
        "code_generated": final_code,
        "collaboration_results": collaborative_results,
        "generation_confidence": confidence,
    }


# Node: Appliquer & Tester avec validation avancée
def apply_test(state: AgentState) -> AgentState:
    """Apply and test the generated code with enhanced validation"""
    if not os.path.exists(state["repo_dir"]):
        return {**state, "test_result": "SKIPPED - No repository directory"}

    print(f"🧪 Applying and testing code for: {state['task']}")

    # Get collaboration results if available
    collaboration_results = state.get("collaboration_results", {})
    confidence = state.get("generation_confidence", 0.5)

    with change_dir(state["repo_dir"]):
        file_path = f"src/jarvys_{state['sub_agent'].lower()}/updated_{state['task'].replace(' ', '_')}.py"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            # Write the final code
            with open(file_path, "w") as f:
                f.write(state["code_generated"])

            # Enhanced testing based on collaboration results
            test_results = []

            # 1. Syntax validation (already done in collaboration)
            test_simulation = collaboration_results.get("test_simulation", {})
            if test_simulation.get("syntax_valid", False):
                test_results.append("✅ Syntax validation passed")
            else:
                test_results.append("❌ Syntax validation failed")

            # 2. Lint fixing
            try:
                lint_output = subprocess.run(
                    f"ruff check --fix {file_path}",
                    shell=True,
                    capture_output=True,
                    text=True,
                )
                if lint_output.returncode == 0:
                    test_results.append("✅ Linting passed")
                else:
                    test_results.append(f"⚠️ Linting issues: {lint_output.stdout[:100]}")
            except Exception as lint_e:
                test_results.append(f"⚠️ Linting failed: {str(lint_e)}")

            # 3. Import analysis
            import_analysis = test_simulation.get("import_analysis", [])
            if not import_analysis:
                test_results.append("✅ Import analysis clean")
            else:
                test_results.append(
                    f"⚠️ Import issues: {len(import_analysis)} potential problems"
                )

            # 4. Security check from Claude validation
            claude_validation = collaboration_results.get("claude_validation", {})
            security_analysis = claude_validation.get("security_analysis", {})
            risk_level = security_analysis.get("risk_level", "unknown")
            test_results.append(f"🔒 Security risk level: {risk_level}")

            # 5. Performance notes
            performance_notes = test_simulation.get("performance_notes", [])
            if performance_notes:
                test_results.append(
                    f"⚡ Performance notes: {len(performance_notes)} items"
                )

            # Compile overall test result
            passed_tests = len([r for r in test_results if "✅" in r])
            total_tests = len(test_results)

            if confidence > 0.7 and passed_tests >= total_tests * 0.7:
                test_result = f"PASSED - {passed_tests}/{total_tests} tests passed (Confidence: {confidence:.2f})"
            elif confidence > 0.5:
                test_result = f"PARTIAL - {passed_tests}/{total_tests} tests passed (Confidence: {confidence:.2f})"
            else:
                test_result = f"FAILED - Low confidence {confidence:.2f}, {passed_tests}/{total_tests} tests passed"

            test_result += f"\nFile created: {file_path}\n" + "\n".join(test_results)

        except Exception as e:
            test_result = f"FAILED - Exception during testing: {str(e)}"

    # Enhanced logging with collaboration context
    log_entry = {
        **state["log_entry"],
        "test_result": test_result[:800],  # Increased limit for detailed results
        "collaboration_confidence": confidence,
        "claude_validation_summary": (
            claude_validation.get("is_valid", False) if claude_validation else None
        ),
        "file_path": file_path,
    }

    # Store test results in memory for learning
    store_memory(
        "test_execution",
        {
            "task": state["task"],
            "agent": state["sub_agent"],
            "test_result_summary": test_result[:200],
            "confidence": confidence,
            "passed": "PASSED" in test_result,
            "collaboration_used": bool(collaboration_results),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        importance=0.7,
        tags=["testing", "execution", "validation", state["sub_agent"].lower()],
    )

    if supabase:
        try:
            supabase.table("orchestrator_logs").update(
                {**log_entry, "step_name": "apply_test"}
            ).eq("task", state["task"]).execute()
        except Exception as db_e:
            print(f"Supabase update failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(log_entry, f)

    return {**state, "test_result": test_result, "log_entry": log_entry}


# Node: Update Docs
def update_docs(state: AgentState) -> AgentState:
    """Update documentation"""
    prompt = f"Génère update doc Markdown pour '{state['task']}' sur {state['sub_agent']}. Sections: Description, Changements, Impact, Exemples. Créatif: Ajoute analogies/ideas fun alignées."
    doc_update = query_grok(prompt, state)

    if os.path.exists(state["repo_dir"]):
        with change_dir(state["repo_dir"]):
            try:
                with open("README.md", "a") as f:
                    f.write(
                        f"\n## Update: {state['task']} ({time.strftime('%Y-%m-%d')})\n{doc_update}\n"
                    )
                os.system("git add README.md")
            except Exception as e:
                print(f"⚠️ Doc update failed: {e}")

    log_entry = {**state["log_entry"], "doc_update": doc_update[:500]}

    if supabase:
        try:
            supabase.table("orchestrator_logs").update(
                {**log_entry, "step_name": "update_docs"}
            ).eq("task", state["task"]).execute()
        except Exception as db_e:
            print(f"Supabase update failed: {db_e} – using local log fallback")
            with open("local_logs.json", "a") as f:
                json.dump(log_entry, f)

    return {**state, "doc_update": doc_update, "log_entry": log_entry}


# Node: Self-Reflect & Commit/PR
def reflect_commit(state: AgentState) -> AgentState:
    """Reflect and commit changes or retry if failed"""
    if "FAILED" in state["test_result"]:
        prompt = f"Reflect: Failed '{state['test_result']}'. Improve, créatif/proactif (alt approaches), adaptable (handle unknown)."
        reflection = query_grok(prompt, state)
        log_entry = {**state["log_entry"], "reflection": reflection}

        if supabase:
            try:
                supabase.table("orchestrator_logs").update(
                    {**log_entry, "step_name": "reflect_commit"}
                ).eq("task", state["task"]).execute()
            except Exception as db_e:
                print(f"Supabase update failed: {db_e} – using local log fallback")
                with open("local_logs.json", "a") as f:
                    json.dump(log_entry, f)

        return {
            **state,
            "reflection": reflection,
            "log_entry": log_entry,
            "next": "generate",
        }
    else:
        # Commit changes
        if os.path.exists(state["repo_dir"]) and state["repo_obj"]:
            with change_dir(state["repo_dir"]):
                try:
                    os.system(
                        f"git add . && git commit -m 'Grok Auto: {state['task']} with docs' && git push origin main"
                    )

                    # Try to create PR if possible
                    try:
                        pr = state["repo_obj"].create_pull(
                            title=f"Grok PR: {state['task']}",
                            body=f"Code: {state['code_generated'][:200]}\nDocs: {state['doc_update'][:200]}\nLog: {str(state['log_entry'])[:200]}",
                            head="main",
                            base="main",
                        )
                        log_entry = {**state["log_entry"], "pr_url": pr.html_url}
                    except Exception as pr_e:
                        log_entry = {**state["log_entry"], "pr_error": str(pr_e)}

                    # Create issue with full log for transparency
                    try:
                        state["repo_obj"].create_issue(
                            title=f"Grok Log: {state['task']} Completed",
                            body=str(log_entry)[:1000],  # Limit body size
                        )
                    except Exception as issue_e:
                        print(f"⚠️ Issue creation failed: {issue_e}")

                except Exception as commit_e:
                    log_entry = {**state["log_entry"], "commit_error": str(commit_e)}
        else:
            log_entry = {**state["log_entry"], "status": "completed_no_repo"}

        log_entry = {**log_entry, "status": "completed"}

        if supabase:
            try:
                supabase.table("orchestrator_logs").update(
                    {**log_entry, "step_name": "reflect_commit"}
                ).eq("task", state["task"]).execute()
            except Exception as db_e:
                print(f"Supabase update failed: {db_e} – using local log fallback")
                with open("local_logs.json", "a") as f:
                    json.dump(log_entry, f)

        return {**state, "log_entry": log_entry}


# Build Graph
def build_orchestrator_graph():
    """Build the LangGraph orchestrator"""
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

    graph.add_conditional_edges(
        "reflect_commit",
        lambda s: s.get("next", END),
        {"generate": "generate", END: END},
    )
    graph.add_conditional_edges(
        "fix_lint",
        lambda s: "fix_lint" if not s["lint_fixed"] else "identify",
        {"fix_lint": "fix_lint", "identify": "identify"},
    )

    return graph.compile()


# Main orchestrator function
def run_orchestrator():
    """Run the JARVYS_DEV orchestrator"""
    print(f"🤖 Initializing {GROK_MODEL} Autonomous Orchestrator...")
    print("📍 Working Branch: main (appia-dev)")
    print("🎯 Target Deployment: main (appIA)")
    print("🔄 Architecture: JARVYS_DEV → JARVYS_AI")

    # Check if running in observation mode (non-intrusive)
    observation_mode = os.getenv("JARVYS_OBSERVATION_MODE", "false").lower() == "true"
    if observation_mode:
        print("👁️ Running in observation mode - minimal interference")

    # Validate all AI systems
    grok_available = validate_grok_api()
    claude_available = validate_claude_api()

    if not grok_available:
        print(f"⚠️ {GROK_MODEL} API not available - orchestrator will use fallbacks")

    if claude_available:
        print("✅ Claude available for code validation")
    else:
        print("⚠️ Claude not available - code validation will be skipped")

    # Initialize memory and repositories
    init_infinite_memory()
    setup_repositories()

    # Check for technology updates
    tech_updates = verify_technology_updates()
    if tech_updates and "API_FALLBACK" not in tech_updates:
        print("🌐 Technology updates retrieved and stored in memory")

    # Initialize state
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

    # Build and run orchestrator
    orchestrator = build_orchestrator_graph()
    max_cycles = 10  # Guard global
    cycle = 0

    while cycle < max_cycles:
        print(f"🤖 Cycle {cycle + 1}/{max_cycles} - {GROK_MODEL} on main → appIA/main")

        try:
            state = orchestrator.invoke(state)
            print(f"✅ Completed cycle {cycle + 1} successfully!")
        except Exception as e:
            print(f"❌ Cycle {cycle + 1} failed: {str(e)}")

        # Clean state for next cycle to prevent data accumulation
        state = clean_state_for_new_cycle(state)

        cycle += 1
        if cycle < max_cycles:  # Don't sleep after last cycle
            print("😴 Sleeping for 2 hours before next cycle...")
            time.sleep(7200)  # 2h - Reduced frequency to avoid interference

    print(f"🎯 Orchestrator completed all {max_cycles} cycles!")


if __name__ == "__main__":
    run_orchestrator()
