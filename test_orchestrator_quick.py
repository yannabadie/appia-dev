#!/usr/bin/env python3
"""
Quick test for Grok Orchestrator - runs one cycle only
"""

import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

# Import orchestrator functions
from grok_orchestrator import (
    ensure_correct_git_setup,
    init_infinite_memory,
    validate_grok_api,
    validate_claude_api,
    verify_technology_updates,
    orchestrator,
    AgentState,
    WORKSPACE_DIR,
    GROK_MODEL,
)


def test_quick_cycle():
    """Run a single orchestrator cycle for testing"""
    print(f"🧪 Quick Test: {GROK_MODEL} Orchestrator")
    print("=" * 50)

    # Initialize systems
    print("1️⃣ Setting up Git...")
    git_ok = ensure_correct_git_setup()
    print(f"   Git setup: {'✅' if git_ok else '❌'}")

    print("2️⃣ Initializing memory...")
    memory_ok = init_infinite_memory()
    print(f"   Memory system: {'✅' if memory_ok else '📝 Local fallback'}")

    print("3️⃣ Validating APIs...")
    grok_ok = validate_grok_api()
    claude_ok = validate_claude_api()
    print(f"   Grok API: {'✅' if grok_ok else '❌'}")
    print(f"   Claude API: {'✅' if claude_ok else '❌'}")

    print("4️⃣ Checking technology updates...")
    tech_updates = verify_technology_updates()
    print(f"   Tech updates: {'✅' if tech_updates else '❌'}")

    print("5️⃣ Running single orchestrator cycle...")

    # Create initial state
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

    try:
        # Run single cycle
        result_state = orchestrator.invoke(state)
        print("✅ Orchestrator cycle completed successfully!")
        print(f"   Task completed: {result_state.get('task', 'N/A')[:50]}...")
        print(f"   Agent: {result_state.get('sub_agent', 'N/A')}")
        print(f"   Lint fixed: {result_state.get('lint_fixed', False)}")
        return True

    except Exception as e:
        print(f"❌ Orchestrator cycle failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_quick_cycle()
    print("=" * 50)
    print(f"🎯 Test result: {'SUCCESS' if success else 'FAILED'}")
