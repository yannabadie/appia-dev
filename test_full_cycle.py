#!/usr/bin/env python3
"""
Test d'un cycle orchestrateur complet JARVYS
Test une tâche réelle avec génération de code, validation et commit
"""
import os
import time
from grok_orchestrator import (
    identify_tasks,
    generate_code, 
    apply_test,
    fix_lint,
    update_docs,
    reflect_commit,
    AgentState,
    clean_state_for_new_cycle,
    log_cycle_step,
    store_memory
)

def test_full_orchestrator_cycle():
    """Test un cycle complet d'orchestration autonome"""
    print("🚀 JARVYS ORCHESTRATOR - CYCLE COMPLET TEST")
    print("=" * 60)
    
    # Initialize cycle
    cycle_number = 1
    start_time = time.time()
    
    # Clean initial state
    initial_state = {
        "task": "",
        "sub_agent": "",
        "repo_dir": "",
        "repo_obj": None,
        "code_generated": "",
        "test_result": "",
        "reflection": "",
        "doc_update": "",
        "log_entry": {},
        "lint_fixed": False
    }
    
    state = clean_state_for_new_cycle(initial_state)
    
    try:
        # Step 1: Identify Tasks
        print(f"\n1️⃣ STEP: IDENTIFY TASKS")
        print("-" * 30)
        log_cycle_step(cycle_number, "identify_tasks", "started")
        
        state = identify_tasks(state)
        
        print(f"📋 Task Identified: {state['task']}")
        print(f"🤖 Sub-Agent: {state['sub_agent']}")
        print(f"📁 Repository: {state['repo_dir']}")
        
        log_cycle_step(cycle_number, "identify_tasks", "completed", f"Task: {state['task']}")
        
        # Step 2: Generate Code
        print(f"\n2️⃣ STEP: GENERATE CODE")
        print("-" * 30)
        log_cycle_step(cycle_number, "generate_code", "started")
        
        state = generate_code(state)
        
        code_length = len(state.get('code_generated', ''))
        confidence = state.get('generation_confidence', 0)
        
        print(f"💻 Code Generated: {code_length} characters")
        print(f"🎯 Generation Confidence: {confidence:.2f}")
        print(f"📝 Code Preview:")
        print(f"   {state.get('code_generated', '')[:150]}...")
        
        log_cycle_step(cycle_number, "generate_code", "completed", f"Code length: {code_length}, Confidence: {confidence}")
        
        # Step 3: Apply & Test
        print(f"\n3️⃣ STEP: APPLY & TEST")
        print("-" * 30)
        log_cycle_step(cycle_number, "apply_test", "started")
        
        state = apply_test(state)
        
        test_result = state.get('test_result', 'NO_RESULT')
        test_passed = 'PASSED' in test_result
        
        print(f"🧪 Test Result: {'✅ PASSED' if test_passed else '⚠️ NEEDS_WORK'}")
        print(f"📊 Test Details: {test_result[:100]}...")
        
        log_cycle_step(cycle_number, "apply_test", "completed" if test_passed else "warning", test_result[:200])
        
        # Step 4: Fix Lint
        print(f"\n4️⃣ STEP: FIX LINT")
        print("-" * 30)
        log_cycle_step(cycle_number, "fix_lint", "started")
        
        state = fix_lint(state)
        
        lint_fixed = state.get('lint_fixed', False)
        print(f"🔧 Lint Status: {'✅ FIXED' if lint_fixed else '⚠️ NEEDS_ATTENTION'}")
        
        log_cycle_step(cycle_number, "fix_lint", "completed" if lint_fixed else "warning")
        
        # Step 5: Update Documentation
        print(f"\n5️⃣ STEP: UPDATE DOCS")
        print("-" * 30)
        log_cycle_step(cycle_number, "update_docs", "started")
        
        state = update_docs(state)
        
        doc_length = len(state.get('doc_update', ''))
        print(f"📚 Documentation: {doc_length} characters generated")
        print(f"📝 Doc Preview: {state.get('doc_update', '')[:100]}...")
        
        log_cycle_step(cycle_number, "update_docs", "completed", f"Doc length: {doc_length}")
        
        # Step 6: Reflect & Commit  
        print(f"\n6️⃣ STEP: REFLECT & COMMIT")
        print("-" * 30)
        log_cycle_step(cycle_number, "reflect_commit", "started")
        
        state = reflect_commit(state)
        
        reflection = state.get('reflection', '')
        reflection_length = len(reflection)
        
        print(f"🤔 Reflection: {reflection_length} characters")
        print(f"💭 Reflection Preview: {reflection[:150]}...")
        
        log_cycle_step(cycle_number, "reflect_commit", "completed", reflection[:200])
        
        # Calculate cycle metrics
        end_time = time.time()
        cycle_duration = end_time - start_time
        
        # Determine overall success
        success_factors = [
            len(state.get('task', '')) > 0,           # Task identified
            code_length > 50,                         # Code generated
            confidence > 0.3,                         # Reasonable confidence
            test_passed or 'SKIPPED' in test_result,  # Test passed or skipped
            lint_fixed,                               # Lint processed
            doc_length > 0                            # Documentation updated
        ]
        
        success_count = sum(success_factors)
        success_rate = (success_count / len(success_factors)) * 100
        
        # Store cycle results in memory
        cycle_results = {
            "cycle_number": cycle_number,
            "task": state['task'],
            "sub_agent": state['sub_agent'],
            "duration_seconds": cycle_duration,
            "success_rate": success_rate,
            "code_generated_length": code_length,
            "generation_confidence": confidence,
            "test_passed": test_passed,
            "lint_fixed": lint_fixed,
            "doc_generated": doc_length > 0,
            "steps_completed": success_count,
            "total_steps": len(success_factors),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        store_memory(
            "cycle_complete",
            cycle_results,
            importance=0.9,
            tags=["orchestrator", "cycle", "testing", "complete"]
        )
        
        # Final Summary
        print(f"\n📊 CYCLE SUMMARY")
        print("=" * 60)
        print(f"⏱️ Duration: {cycle_duration:.1f} seconds")
        print(f"✅ Steps Completed: {success_count}/{len(success_factors)}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"🎯 Code Generation Confidence: {confidence:.2f}")
        print(f"📋 Task: {state['task']}")
        print(f"🤖 Agent: {state['sub_agent']}")
        
        if success_rate >= 80:
            print("🎉 CYCLE STATUS: EXCELLENT")
        elif success_rate >= 60:
            print("👍 CYCLE STATUS: GOOD") 
        else:
            print("⚠️ CYCLE STATUS: NEEDS IMPROVEMENT")
            
        return cycle_results
        
    except Exception as e:
        print(f"❌ CYCLE FAILED: {str(e)}")
        log_cycle_step(cycle_number, "cycle_error", "failed", str(e))
        
        # Store failure for learning
        store_memory(
            "cycle_error",
            {
                "cycle_number": cycle_number,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "partial_state": {
                    "task": state.get('task', ''),
                    "sub_agent": state.get('sub_agent', ''),
                    "steps_completed": len([k for k in state.keys() if state.get(k)])
                }
            },
            importance=0.8,
            tags=["error", "cycle", "learning"]
        )
        
        return {"error": str(e), "cycle_number": cycle_number}

if __name__ == "__main__":
    print("🏁 Starting Full Orchestrator Cycle Test...")
    result = test_full_orchestrator_cycle()
    print(f"\n🏆 FINAL RESULT:")
    
    if "error" in result:
        print(f"❌ Cycle failed: {result['error']}")
    else:
        print(f"✅ Success Rate: {result['success_rate']:.1f}%")
        print(f"⏱️ Duration: {result['duration_seconds']:.1f}s")
        print(f"📋 Task: {result['task']}")
        
    print(f"\n🔚 Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
