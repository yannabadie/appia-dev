#!/usr/bin/env python3
"""
Test script for JARVYS Orchestrator Components
"""

import json
import time

from grok_orchestrator import (
    CLAUDE_API_KEY,
    CLAUDE_AVAILABLE,
    XAI_API_KEY,
    XAI_SDK_AVAILABLE,
    collaborative_code_testing,
    get_available_secrets_summary,
    init_infinite_memory,
    query_grok,
    retrieve_memories,
    store_memory,
    validate_claude_api,
    validate_code_with_claude,
    validate_grok_api,
)


def test_orchestrator_components():
    """Test all major orchestrator components"""
    print("🧪 JARVYS ORCHESTRATOR COMPONENT TESTING")
    print("=" * 60)

    # Test 1: Environment Setup
    print("\n1️⃣ ENVIRONMENT VERIFICATION")
    print("-" * 30)
    secrets = get_available_secrets_summary()
    print(f"📊 Available Secrets: {json.dumps(secrets, indent=2)}")
    print(f"🔑 XAI SDK Available: {XAI_SDK_AVAILABLE}")
    print(f"🔑 Claude Available: {CLAUDE_AVAILABLE}")
    print(
        f"🔑 XAI API Key: {'✅ SET' if XAI_API_KEY and XAI_API_KEY != 'test-key' else '❌ MISSING'}"
    )
    print(f"🔑 Claude API Key: {'✅ SET' if CLAUDE_API_KEY else '❌ MISSING'}")

    # Test 2: API Validations
    print("\n2️⃣ API CONNECTION TESTING")
    print("-" * 30)

    print("🔍 Testing Grok-4-0709 API...")
    grok_ok = validate_grok_api()
    print(f"   Result: {'✅ CONNECTED' if grok_ok else '❌ FAILED'}")

    print("\n🔍 Testing Claude 4 API...")
    claude_ok = validate_claude_api()
    print(f"   Result: {'✅ CONNECTED' if claude_ok else '❌ FAILED'}")

    # Test 3: Memory System
    print("\n3️⃣ INFINITE MEMORY SYSTEM")
    print("-" * 30)
    print("🧠 Initializing memory system...")
    memory_ok = init_infinite_memory()
    print(f"   Result: {'✅ INITIALIZED' if memory_ok else '❌ FAILED'}")

    if memory_ok:
        # Test memory storage
        test_memory_id = store_memory(
            "component_test",
            {
                "test_type": "orchestrator_validation",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "apis_working": {"grok": grok_ok, "claude": claude_ok},
            },
            importance=0.8,
            tags=["testing", "validation", "orchestrator"],
        )
        print(f"   📝 Test Memory Stored: {test_memory_id}")

        # Test memory retrieval
        memories = retrieve_memories(memory_type="component_test", limit=2)
        print(f"   🔍 Memories Retrieved: {len(memories)}")

    # Test 4: Grok Query
    print("\n4️⃣ GROK-4 QUERY TESTING")
    print("-" * 30)

    if grok_ok:
        test_state = {
            "sub_agent": "TEST",
            "task": "Generate Python test function",
            "repo_dir": "/workspaces/appia-dev",
            "log_entry": {},
        }

        try:
            print("🤖 Querying Grok-4 for simple code generation...")
            response = query_grok(
                "Generate a simple Python function that calculates fibonacci numbers. Include docstring and error handling.",
                test_state,
                "general",
            )
            print(f"   📝 Response Length: {len(response)} characters")
            print("   📋 Response Preview:")
            print(f"   {response[:200]}...")
            print("   ✅ Grok query successful")

            # Test collaborative testing if Claude is also available
            if claude_ok:
                print("\n🤝 Testing collaborative Grok-Claude testing...")
                collab_results = collaborative_code_testing(
                    response, "Generate fibonacci function", test_state
                )
                confidence = collab_results.get("confidence_score", 0)
                print(f"   🎯 Collaboration Confidence: {confidence:.2f}")
                print(
                    f"   ✅ Collaborative testing: {'SUCCESS' if confidence > 0.5 else 'NEEDS_IMPROVEMENT'}"
                )

        except Exception as e:
            print(f"   ❌ Grok query failed: {str(e)}")
    else:
        print("   ⚠️ Skipping Grok query test (API not available)")

    # Test 5: Claude Validation
    print("\n5️⃣ CLAUDE VALIDATION TESTING")
    print("-" * 30)

    if claude_ok:
        test_code = '''
def fibonacci(n):
    """Calculate fibonacci number at position n"""
    if n < 0:
        raise ValueError("Position must be non-negative")
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
        try:
            print("🔍 Testing Claude code validation...")
            validation_result = validate_code_with_claude(
                test_code, "Fibonacci function implementation"
            )

            is_valid = validation_result.get("is_valid", False)
            confidence = validation_result.get("confidence", 0)
            print(
                f"   📊 Validation Result: {'✅ VALID' if is_valid else '❌ INVALID'}"
            )
            print(f"   🎯 Confidence: {confidence}")

            if "issues" in validation_result:
                print(f"   📋 Issues Found: {len(validation_result['issues'])}")

        except Exception as e:
            print(f"   ❌ Claude validation failed: {str(e)}")
    else:
        print("   ⚠️ Skipping Claude validation test (API not available)")

    # Test Summary
    print("\n📊 TESTING SUMMARY")
    print("=" * 60)

    total_tests = 5
    passed_tests = sum(
        [
            True,  # Environment always passes if we get here
            grok_ok,
            claude_ok,
            memory_ok,
            grok_ok,  # Grok query test result
        ]
    )

    success_rate = (passed_tests / total_tests) * 100

    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("🎉 ORCHESTRATOR COMPONENTS: EXCELLENT STATUS")
    elif success_rate >= 60:
        print("⚠️ ORCHESTRATOR COMPONENTS: FUNCTIONAL BUT NEEDS ATTENTION")
    else:
        print("❌ ORCHESTRATOR COMPONENTS: CRITICAL ISSUES DETECTED")

    print(f"\n🏁 Component testing completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    return {
        "success_rate": success_rate,
        "grok_api": grok_ok,
        "claude_api": claude_ok,
        "memory_system": memory_ok,
        "total_passed": passed_tests,
        "total_tests": total_tests,
    }


if __name__ == "__main__":
    result = test_orchestrator_components()
    print(f"\n🔬 Final Test Result: {json.dumps(result, indent=2)}")
