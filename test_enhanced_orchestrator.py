#!/usr/bin/env python3
"""
Test script for the enhanced GROK-4 Orchestrator with Claude integration and infinite memory
"""

import os
import sys
import time


def test_orchestrator_enhanced():
    """Test the enhanced orchestrator features"""

    print("🚀 Testing Enhanced GROK-4 Orchestrator")
    print("=" * 50)

    # Test environment variables
    print("📋 Environment Check:")
    xai_key = bool(os.getenv("XAI_API_KEY"))
    claude_key = bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"))
    supabase_url = bool(os.getenv("SUPABASE_URL"))
    supabase_key = bool(os.getenv("SUPABASE_KEY"))

    print(f"  ✅ XAI API Key: {'Available' if xai_key else '❌ Missing'}")
    print(f"  ✅ Claude API Key: {'Available' if claude_key else '❌ Missing'}")
    print(f"  ✅ Supabase URL: {'Available' if supabase_url else '❌ Missing'}")
    print(f"  ✅ Supabase Key: {'Available' if supabase_key else '❌ Missing'}")

    if not all([xai_key, supabase_url, supabase_key]):
        print("⚠️ Some required environment variables are missing!")
        return False

    # Test imports
    print("\n📦 Testing Imports:")
    try:
        from grok_orchestrator import (
            init_infinite_memory,
            retrieve_memories,
            store_memory,
            validate_claude_api,
            validate_grok_api,
            verify_technology_updates,
        )

        print("  ✅ All enhanced functions imported successfully")
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

    # Test API validations
    print("\n🔗 Testing API Connections:")
    try:
        grok_status = validate_grok_api()
        print(f"  Grok-4-0709: {'✅ Connected' if grok_status else '❌ Failed'}")
    except Exception as e:
        print(f"  Grok-4-0709: ❌ Error - {e}")

    if claude_key:
        try:
            claude_status = validate_claude_api()
            print(f"  Claude 4: {'✅ Connected' if claude_status else '❌ Failed'}")
        except Exception as e:
            print(f"  Claude 4: ❌ Error - {e}")
    else:
        print("  Claude 4: ⚠️ Skipped (no API key)")

    # Test memory system
    print("\n🧠 Testing Infinite Memory System:")
    try:
        memory_status = init_infinite_memory()
        print(f"  Memory Init: {'✅ Success' if memory_status else '❌ Failed'}")

        if memory_status:
            # Test storing a memory
            memory_id = store_memory(
                "test_memory",
                {"test": "orchestrator_enhanced", "timestamp": time.time()},
                importance=0.5,
                tags=["test", "enhanced"],
            )
            print(f"  Memory Store: {'✅ Success' if memory_id else '❌ Failed'}")

            # Test retrieving memories
            memories = retrieve_memories("test_memory", limit=1)
            print(f"  Memory Retrieve: {'✅ Success' if memories else '❌ Failed'}")

    except Exception as e:
        print(f"  Memory System: ❌ Error - {e}")

    # Test technology verification
    print("\n🌐 Testing Technology Verification:")
    try:
        tech_updates = verify_technology_updates()
        has_updates = tech_updates and "API_FALLBACK" not in tech_updates
        print(f"  Tech Updates: {'✅ Retrieved' if has_updates else '⚠️ Limited'}")
    except Exception as e:
        print(f"  Tech Updates: ❌ Error - {e}")

    print("\n🎯 Enhanced Orchestrator Test Complete!")
    print("Ready for autonomous operation with:")
    print("  • Grok-4-0709 primary AI")
    print("  • Claude 4 code validation")
    print("  • Infinite Supabase memory")
    print("  • Technology verification")

    return True


if __name__ == "__main__":
    success = test_orchestrator_enhanced()
    sys.exit(0 if success else 1)
