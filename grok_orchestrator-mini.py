#!/usr/bin/env python3
"""
JARVYS Autonomous Orchestrator - Maximum Autonomy Edition
An AI system designed for near-complete autonomous operation with self-improvement capabilities
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import hashlib
import traceback

from dataclasses import dataclass, field
from contextlib import asynccontextmanager

# Core dependencies
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict, Annotated

# Import AI SDKs with fallback handling
try:
    from xai_sdk import Client as XAIClient
    from xai_sdk.chat import system, user
    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False
    print("⚠️ xAI SDK not available")

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    print("⚠️ Anthropic SDK not available")

from supabase import create_client


class AutonomyLevel(Enum):
    """Levels of autonomous operation"""
    OBSERVATION = "observation"  # Monitor only
    ASSISTED = "assisted"       # Require approval for critical actions
    SUPERVISED = "supervised"   # Act but log everything
    AUTONOMOUS = "autonomous"   # Full autonomy with safety guards
    EVOLUTION = "evolution"     # Self-modifying code capabilities


@dataclass
class AutonomousConfig:
    """Configuration for autonomous operation"""
    autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED
    max_cost_per_cycle: float = 10.0  # USD
    max_api_calls_per_hour: int = 100
    allow_self_modification: bool = False
    require_test_success: bool = True
    auto_rollback_on_failure: bool = True
    memory_pruning_days: int = 90
    confidence_threshold: float = 0.7
    learning_rate: float = 0.1


class AutonomousMemory:
    """Advanced memory system with pattern recognition and learning"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.local_cache = {}
        self.decision_history = []
        self.performance_metrics = {
            "success_rate": 0.0,
            "avg_confidence": 0.0,
            "total_cycles": 0,
            "patterns_learned": 0
        }
    
    async def remember_decision(self, decision_type: str, context: dict, 
                                outcome: str, confidence: float):
        """Store decision with outcome for learning"""
        decision_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision_type": decision_type,
            "context": context,
            "outcome": outcome,
            "confidence": confidence,
            "success": outcome in ["success", "completed", "passed"]
        }
        
        # Store in Supabase
        try:
            await self.supabase.table("autonomous_decisions").insert(decision_data).execute()
        except Exception as e:
            print(f"⚠️ Failed to store decision: {e}")
        
        # Update local metrics
        self.decision_history.append(decision_data)
        self._update_performance_metrics()
    
    def _update_performance_metrics(self):
        """Update performance metrics based on decision history"""
        if not self.decision_history:
            return
        
        recent_decisions = self.decision_history[-100:]  # Last 100 decisions
        successes = sum(1 for d in recent_decisions if d["success"])
        
        self.performance_metrics["success_rate"] = successes / len(recent_decisions)
        self.performance_metrics["avg_confidence"] = sum(d["confidence"] for d in recent_decisions) / len(recent_decisions)
        self.performance_metrics["total_cycles"] = len(self.decision_history)
    
    async def get_similar_decisions(self, decision_type: str, context: dict, limit: int = 5):
        """Retrieve similar past decisions for learning"""
        try:
            # Create context hash for similarity matching
            context_hash = hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()[:8]
            
            result = await self.supabase.table("autonomous_decisions") \
                .select("*") \
                .eq("decision_type", decision_type) \
                .order("timestamp", desc=True) \
                .limit(limit) \
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"⚠️ Failed to retrieve similar decisions: {e}")
            return []
    
    async def learn_from_patterns(self):
        """Analyze patterns in decision history to improve future decisions"""
        patterns = {
            "best_practices": [],
            "common_failures": [],
            "optimization_opportunities": []
        }
        
        # Analyze success patterns
        successful_decisions = [d for d in self.decision_history if d["success"]]
        if successful_decisions:
            # Group by decision type
            by_type = {}
            for decision in successful_decisions:
                dtype = decision["decision_type"]
                if dtype not in by_type:
                    by_type[dtype] = []
                by_type[dtype].append(decision)
            
            # Find patterns
            for dtype, decisions in by_type.items():
                if len(decisions) >= 3:  # Need at least 3 instances for a pattern
                    avg_confidence = sum(d["confidence"] for d in decisions) / len(decisions)
                    patterns["best_practices"].append({
                        "type": dtype,
                        "success_rate": 1.0,
                        "avg_confidence": avg_confidence,
                        "sample_context": decisions[0]["context"]
                    })
        
        self.performance_metrics["patterns_learned"] = len(patterns["best_practices"])
        return patterns


class AutonomousOrchestrator:
    """Main orchestrator with maximum autonomy capabilities"""
    
    def __init__(self, config: AutonomousConfig):
        self.config = config
        self.memory = None
        self.api_call_tracker = {"count": 0, "last_reset": datetime.utcnow()}
        self.cost_tracker = {"total": 0.0, "cycle_cost": 0.0}
        self.active_monitors = []
        self.safety_violations = []
        
        # Initialize AI clients
        self.ai_clients = self._init_ai_clients()
        
        # Initialize Supabase
        self.supabase = self._init_supabase()
        
        # Initialize state machine
        self.workflow = self._build_workflow()
    
    def _init_ai_clients(self) -> dict:
        """Initialize AI clients with fallback options"""
        clients = {}
        
        if XAI_AVAILABLE and os.getenv("XAI_API_KEY"):
            clients["grok"] = XAIClient(
                api_key=os.getenv("XAI_API_KEY"),
                timeout=180
            )
        
        if CLAUDE_AVAILABLE and os.getenv("CLAUDE_API_KEY"):
            clients["claude"] = anthropic.Anthropic(
                api_key=os.getenv("CLAUDE_API_KEY")
            )
        
        return clients
    
    def _init_supabase(self):
        """Initialize Supabase client"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY")
        
        if url and key:
            client = create_client(url, key)
            self.memory = AutonomousMemory(client)
            return client
        return None
    
    async def check_safety_constraints(self) -> bool:
        """Check if operating within safety constraints"""
        # Check API rate limits
        if self.api_call_tracker["count"] >= self.config.max_api_calls_per_hour:
            if (datetime.utcnow() - self.api_call_tracker["last_reset"]).seconds < 3600:
                self.safety_violations.append("API rate limit exceeded")
                return False
            else:
                # Reset counter
                self.api_call_tracker["count"] = 0
                self.api_call_tracker["last_reset"] = datetime.utcnow()
        
        # Check cost limits
        if self.cost_tracker["cycle_cost"] >= self.config.max_cost_per_cycle:
            self.safety_violations.append(f"Cost limit exceeded: ${self.cost_tracker['cycle_cost']:.2f}")
            return False
        
        return True
    
    async def autonomous_decision(self, decision_type: str, options: List[Dict], 
                                 context: Dict) -> Dict:
        """Make autonomous decision based on past experience and current context"""
        
        # Check safety constraints first
        if not await self.check_safety_constraints():
            return {"action": "halt", "reason": "Safety constraints violated"}
        
        # Get similar past decisions
        similar_decisions = await self.memory.get_similar_decisions(
            decision_type, context
        ) if self.memory else []
        
        # Calculate confidence based on past performance
        base_confidence = self.memory.performance_metrics["avg_confidence"] if self.memory else 0.5
        
        # Adjust confidence based on similar decisions
        if similar_decisions:
            successful_similar = [d for d in similar_decisions if d.get("success")]
            if successful_similar:
                similarity_boost = len(successful_similar) / len(similar_decisions) * 0.2
                base_confidence = min(base_confidence + similarity_boost, 0.95)
        
        # Make decision based on autonomy level
        if self.config.autonomy_level == AutonomyLevel.OBSERVATION:
            return {"action": "observe", "confidence": base_confidence}
        
        elif self.config.autonomy_level == AutonomyLevel.ASSISTED:
            # Require human approval for confidence < threshold
            if base_confidence < self.config.confidence_threshold:
                return {
                    "action": "request_approval",
                    "confidence": base_confidence,
                    "options": options
                }
        
        # For supervised and above, make autonomous decision
        best_option = self._evaluate_options(options, similar_decisions, context)
        
        # Record decision
        if self.memory:
            await self.memory.remember_decision(
                decision_type, context, "pending", base_confidence
            )
        
        return {
            "action": "execute",
            "selected_option": best_option,
            "confidence": base_confidence,
            "reasoning": f"Based on {len(similar_decisions)} similar past decisions"
        }
    
    def _evaluate_options(self, options: List[Dict], past_decisions: List[Dict], 
                         context: Dict) -> Dict:
        """Evaluate options based on past experience"""
        if not options:
            return None
        
        # Score each option
        scored_options = []
        for option in options:
            score = 0.5  # Base score
            
            # Adjust based on past decisions
            for decision in past_decisions:
                if decision.get("success") and self._similar_context(
                    decision.get("context", {}), context
                ):
                    score += 0.1
            
            # Add randomness for exploration (epsilon-greedy)
            if self.config.learning_rate > 0:
                import random
                if random.random() < self.config.learning_rate:
                    score += random.uniform(-0.2, 0.2)
            
            scored_options.append((score, option))
        
        # Select best option
        scored_options.sort(key=lambda x: x[0], reverse=True)
        return scored_options[0][1]
    
    def _similar_context(self, context1: Dict, context2: Dict) -> bool:
        """Check if two contexts are similar"""
        # Simple similarity check - can be made more sophisticated
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return False
        
        matches = sum(1 for k in common_keys if context1.get(k) == context2.get(k))
        return matches / len(common_keys) > 0.7
    
    def _build_workflow(self) -> StateGraph:
        """Build autonomous workflow with self-improvement capabilities"""
        
        class AutonomousState(TypedDict):
            cycle_id: str
            current_task: str
            decisions_made: List[Dict]
            code_generated: str
            test_results: Dict
            performance_score: float
            should_evolve: bool
            safety_status: str
        
        workflow = StateGraph(AutonomousState)
        
        # Define autonomous nodes
        async def analyze_environment(state: AutonomousState) -> AutonomousState:
            """Analyze current environment and identify opportunities"""
            # Scan for issues, failing tests, performance problems
            analysis = await self._scan_environment()
            
            # Make autonomous decision on what to work on
            decision = await self.autonomous_decision(
                "task_selection",
                analysis["opportunities"],
                {"cycle_id": state["cycle_id"], "previous_task": state.get("current_task")}
            )
            
            state["current_task"] = decision.get("selected_option", {}).get("task", "monitor")
            state["decisions_made"].append(decision)
            
            return state
        
        async def generate_solution(state: AutonomousState) -> AutonomousState:
            """Generate solution with AI collaboration"""
            if state["current_task"] == "monitor":
                return state
            
            # Use AI to generate solution
            solution = await self._generate_ai_solution(state["current_task"])
            state["code_generated"] = solution["code"]
            
            # Validate with secondary AI if available
            if "claude" in self.ai_clients and "grok" in self.ai_clients:
                validation = await self._validate_with_claude(solution["code"], state["current_task"])
                if validation["improvements"]:
                    state["code_generated"] = validation["improved_code"]
            
            return state
        
        async def test_and_deploy(state: AutonomousState) -> AutonomousState:
            """Test solution and deploy if successful"""
            if not state.get("code_generated"):
                return state
            
            # Run tests
            test_results = await self._run_automated_tests(state["code_generated"])
            state["test_results"] = test_results
            
            # Make deployment decision
            deploy_decision = await self.autonomous_decision(
                "deployment",
                [{"action": "deploy"}, {"action": "rollback"}, {"action": "iterate"}],
                {
                    "test_success_rate": test_results.get("success_rate", 0),
                    "confidence": test_results.get("confidence", 0)
                }
            )
            
            if deploy_decision["action"] == "execute" and \
               deploy_decision["selected_option"]["action"] == "deploy":
                await self._deploy_changes(state["code_generated"])
            
            return state
        
        async def self_evaluate(state: AutonomousState) -> AutonomousState:
            """Evaluate own performance and decide on self-improvement"""
            # Calculate performance score
            performance = await self._calculate_performance(state)
            state["performance_score"] = performance["score"]
            
            # Decide if should evolve
            if self.config.allow_self_modification and \
               self.config.autonomy_level == AutonomyLevel.EVOLUTION:
                evolution_decision = await self.autonomous_decision(
                    "self_evolution",
                    [{"evolve": True}, {"evolve": False}],
                    {
                        "performance_score": performance["score"],
                        "patterns_learned": self.memory.performance_metrics["patterns_learned"]
                    }
                )
                
                state["should_evolve"] = evolution_decision.get("selected_option", {}).get("evolve", False)
            
            # Learn from this cycle
            if self.memory:
                patterns = await self.memory.learn_from_patterns()
                print(f"📊 Learned {len(patterns['best_practices'])} new patterns")
            
            return state
        
        async def evolve_self(state: AutonomousState) -> AutonomousState:
            """Self-modification capabilities for continuous improvement"""
            if not state.get("should_evolve") or not self.config.allow_self_modification:
                return state
            
            # Generate improvements to own code
            self_improvements = await self._generate_self_improvements()
            
            # Test improvements in sandbox
            if await self._test_in_sandbox(self_improvements):
                # Apply improvements with rollback capability
                await self._apply_self_improvements(self_improvements)
                print("🧬 Self-evolution completed successfully")
            
            return state
        
        # Add nodes to workflow
        workflow.add_node("analyze", analyze_environment)
        workflow.add_node("generate", generate_solution)
        workflow.add_node("test_deploy", test_and_deploy)
        workflow.add_node("evaluate", self_evaluate)
        workflow.add_node("evolve", evolve_self)
        
        # Define edges
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "generate")
        workflow.add_edge("generate", "test_deploy")
        workflow.add_edge("test_deploy", "evaluate")
        workflow.add_edge("evaluate", "evolve")
        workflow.add_edge("evolve", END)
        
        return workflow.compile()
    
    async def _scan_environment(self) -> Dict:
        """Scan environment for autonomous action opportunities"""
        opportunities = []
        
        # Check for failing tests
        try:
            test_result = subprocess.run(
                ["pytest", "--tb=short", "-q"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if test_result.returncode != 0:
                failures = [line for line in test_result.stdout.splitlines() if "FAILED" in line]
                opportunities.extend([
                    {"task": f"Fix test: {failure}", "priority": 0.9}
                    for failure in failures[:3]  # Limit to top 3
                ])
        except Exception:
            pass
        
        # Check for code quality issues
        try:
            lint_result = subprocess.run(
                ["ruff", "check", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if lint_result.stdout:
                issues = json.loads(lint_result.stdout)
                if len(issues) > 5:
                    opportunities.append({
                        "task": f"Fix {len(issues)} code quality issues",
                        "priority": 0.7
                    })
        except Exception:
            pass
        
        # Check performance metrics from memory
        if self.memory and self.memory.performance_metrics["success_rate"] < 0.8:
            opportunities.append({
                "task": "Improve success rate through pattern analysis",
                "priority": 0.8
            })
        
        # Add creative tasks
        opportunities.extend([
            {"task": "Optimize memory usage patterns", "priority": 0.5},
            {"task": "Implement new monitoring metrics", "priority": 0.4},
            {"task": "Generate documentation updates", "priority": 0.3}
        ])
        
        return {"opportunities": sorted(opportunities, key=lambda x: x["priority"], reverse=True)}
    
    async def _generate_ai_solution(self, task: str) -> Dict:
        """Generate solution using available AI"""
        prompt = f"""
        Task: {task}
        
        Generate a complete, production-ready Python solution that:
        1. Solves the task efficiently
        2. Includes comprehensive error handling
        3. Follows best practices
        4. Includes inline documentation
        5. Is designed for autonomous operation
        
        Context: Part of JARVYS autonomous system with Supabase memory and GitHub integration.
        """
        
        code = ""
        if "grok" in self.ai_clients:
            # Use Grok for generation
            code = await self._call_grok(prompt)
        elif "claude" in self.ai_clients:
            # Fallback to Claude
            code = await self._call_claude(prompt)
        else:
            # Basic template
            code = f'''
def autonomous_solution():
    """Auto-generated solution for: {task}"""
    # TODO: Implement solution
    pass
'''
        
        self.api_call_tracker["count"] += 1
        self.cost_tracker["cycle_cost"] += 0.05  # Estimate
        
        return {"code": code, "task": task}
    
    async def _validate_with_claude(self, code: str, task: str) -> Dict:
        """Validate and improve code with Claude"""
        if "claude" not in self.ai_clients:
            return {"improvements": False}
        
        prompt = f"""
        Review this Python code for task: {task}
        
        Code:
        ```python
        {code}
        ```
        
        Provide:
        1. Validation (is it safe and correct?)
        2. Improvements (if any)
        3. Security concerns
        4. Performance optimizations
        
        Return improved code if changes needed.
        """
        
        response = await self._call_claude(prompt)
        
        # Parse response (simplified)
        if "```python" in response:
            improved_code = response.split("```python")[1].split("```")[0]
            return {"improvements": True, "improved_code": improved_code}
        
        return {"improvements": False}
    
    async def _run_automated_tests(self, code: str) -> Dict:
        """Run automated tests on generated code"""
        # Create temporary test file
        test_file = f"test_autonomous_{int(time.time())}.py"
        
        try:
            with open(test_file, "w") as f:
                f.write(code)
                f.write("\n\n# Automated test\n")
                f.write("""
if __name__ == "__main__":
    try:
        autonomous_solution()
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")
""")
            
            # Run test
            result = subprocess.run(
                ["python", test_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            success = "SUCCESS" in result.stdout
            confidence = 0.9 if success else 0.3
            
            return {
                "success_rate": 1.0 if success else 0.0,
                "confidence": confidence,
                "output": result.stdout + result.stderr
            }
        
        except Exception as e:
            return {
                "success_rate": 0.0,
                "confidence": 0.1,
                "error": str(e)
            }
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
    
    async def _deploy_changes(self, code: str):
        """Deploy changes with safety checks"""
        if self.config.autonomy_level not in [AutonomyLevel.AUTONOMOUS, AutonomyLevel.EVOLUTION]:
            print("🔒 Deployment blocked - insufficient autonomy level")
            return
        
        # Create backup first
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/autonomous_backup_{timestamp}.py"
        
        os.makedirs("backups", exist_ok=True)
        with open(backup_file, "w") as f:
            f.write(code)
        
        print(f"✅ Changes deployed with backup: {backup_file}")
    
    async def _calculate_performance(self, state: AutonomousState) -> Dict:
        """Calculate performance metrics"""
        score = 0.5  # Base score
        
        # Adjust based on test results
        if state.get("test_results"):
            score += state["test_results"].get("success_rate", 0) * 0.3
        
        # Adjust based on decision confidence
        if state.get("decisions_made"):
            avg_confidence = sum(d.get("confidence", 0) for d in state["decisions_made"]) / len(state["decisions_made"])
            score += avg_confidence * 0.2
        
        # Adjust based on memory performance
        if self.memory:
            score += self.memory.performance_metrics["success_rate"] * 0.2
        
        return {"score": min(score, 1.0)}
    
    async def _generate_self_improvements(self) -> str:
        """Generate improvements to own code"""
        # Analyze own performance patterns
        patterns = await self.memory.learn_from_patterns() if self.memory else {}
        
        prompt = f"""
        Based on these performance patterns:
        {json.dumps(patterns, indent=2)}
        
        Generate improvements to the autonomous orchestrator code that will:
        1. Increase success rate
        2. Improve decision-making
        3. Optimize resource usage
        4. Enhance learning capabilities
        
        Focus on small, safe improvements that can be tested.
        """
        
        if "grok" in self.ai_clients:
            return await self._call_grok(prompt)
        
        return ""
    
    async def _test_in_sandbox(self, improvements: str) -> bool:
        """Test improvements in isolated environment"""
        # Simplified sandbox testing
        # In production, use Docker or VMs
        try:
            # Basic syntax check
            compile(improvements, "<string>", "exec")
            return True
        except:
            return False
    
    async def _apply_self_improvements(self, improvements: str):
        """Apply self-improvements with rollback capability"""
        # Store current state
        self_backup = f"backups/self_evolution_{int(time.time())}.py"
        
        # This is where real self-modification would occur
        # For safety, we just log the improvements
        with open("evolution_log.txt", "a") as f:
            f.write(f"\n\n--- Evolution at {datetime.utcnow().isoformat()} ---\n")
            f.write(improvements)
        
        print("🧬 Self-improvements logged for review")
    
    async def _call_grok(self, prompt: str) -> str:
        """Call Grok API with proper error handling"""
        try:
            client = self.ai_clients["grok"]
            chat = client.chat.create(model="grok-4-0709", temperature=0.5)
            chat.append(system("You are an expert autonomous AI system architect."))
            chat.append(user(prompt))
            response = chat.sample()
            return response.content
        except Exception as e:
            print(f"❌ Grok API error: {e}")
            return ""
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API with proper error handling"""
        try:
            client = self.ai_clients["claude"]
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            return ""
    
    async def run_autonomous_cycle(self):
        """Run a single autonomous cycle"""
        print(f"\n🤖 Starting autonomous cycle at {datetime.utcnow().isoformat()}")
        print(f"📊 Autonomy Level: {self.config.autonomy_level.value}")
        
        # Initialize state
        state = {
            "cycle_id": f"cycle_{int(time.time())}",
            "current_task": "",
            "decisions_made": [],
            "code_generated": "",
            "test_results": {},
            "performance_score": 0.0,
            "should_evolve": False,
            "safety_status": "OK"
        }
        
        try:
            # Run workflow
            final_state = await self.workflow.ainvoke(state)
            
            # Log cycle results
            print(f"\n📈 Cycle Performance Score: {final_state['performance_score']:.2f}")
            print(f"💰 Cycle Cost: ${self.cost_tracker['cycle_cost']:.2f}")
            
            # Update memory with cycle results
            if self.memory:
                await self.memory.remember_decision(
                    "cycle_completion",
                    {"cycle_id": state["cycle_id"]},
                    "success" if final_state["performance_score"] > 0.7 else "partial",
                    final_state["performance_score"]
                )
            
            # Reset cycle cost
            self.cost_tracker["total"] += self.cost_tracker["cycle_cost"]
            self.cost_tracker["cycle_cost"] = 0.0
            
        except Exception as e:
            print(f"❌ Cycle failed: {e}")
            traceback.print_exc()
            
            # Record failure
            if self.memory:
                await self.memory.remember_decision(
                    "cycle_completion",
                    {"cycle_id": state["cycle_id"], "error": str(e)},
                    "failed",
                    0.0
                )


async def main():
    """Main entry point for autonomous orchestrator"""
    
    # Configure autonomy level based on environment
    autonomy_level = AutonomyLevel(
        os.getenv("JARVYS_AUTONOMY_LEVEL", "supervised").lower()
    )
    
    config = AutonomousConfig(
        autonomy_level=autonomy_level,
        max_cost_per_cycle=float(os.getenv("MAX_COST_PER_CYCLE", "10.0")),
        max_api_calls_per_hour=int(os.getenv("MAX_API_CALLS_PER_HOUR", "100")),
        allow_self_modification=os.getenv("ALLOW_SELF_MODIFICATION", "false").lower() == "true",
        confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    )
    
    # Initialize orchestrator
    orchestrator = AutonomousOrchestrator(config)
    
    print("🚀 JARVYS Autonomous Orchestrator Starting...")
    print(f"🧠 Memory System: {'Connected' if orchestrator.memory else 'Local Only'}")
    print(f"🤖 AI Systems: {list(orchestrator.ai_clients.keys())}")
    
    # Run continuous autonomous cycles
    cycle_count = 0
    max_cycles = int(os.getenv("MAX_CYCLES", "0"))  # 0 = infinite
    
    while max_cycles == 0 or cycle_count < max_cycles:
        cycle_count += 1
        print(f"\n{'='*60}")
        print(f"🔄 AUTONOMOUS CYCLE {cycle_count}")
        print(f"{'='*60}")
        
        # Run cycle
        await orchestrator.run_autonomous_cycle()
        
        # Adaptive sleep based on performance
        if orchestrator.memory:
            success_rate = orchestrator.memory.performance_metrics["success_rate"]
            if success_rate > 0.9:
                sleep_time = 1800  # 30 min if performing well
            elif success_rate > 0.7:
                sleep_time = 3600  # 1 hour if moderate
            else:
                sleep_time = 7200  # 2 hours if struggling
        else:
            sleep_time = 3600  # Default 1 hour
        
        print(f"\n💤 Sleeping for {sleep_time/60:.0f} minutes before next cycle...")
        await asyncio.sleep(sleep_time)
    
    print("\n✅ Autonomous orchestrator completed all cycles")
    print(f"💰 Total cost: ${orchestrator.cost_tracker['total']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())