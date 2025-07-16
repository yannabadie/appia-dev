#!/usr/bin/env python3
"""
Orchestrator Monitor - Non-intrusive observation system
Surveys GROK orchestrator activity without interfering with operations
"""

import json
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List


class OrchestrationMonitor:
    def __init__(self):
        self.workspace_dir = "/workspaces/appia-dev"
        self.log_file = os.path.join(self.workspace_dir, "local_logs.json")
        self.last_log_count = 0
        self.monitoring = True

    def get_orchestrator_status(self) -> Dict:
        """Check if orchestrator is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "grok_orchestrator.py"], capture_output=True, text=True
            )
            is_running = len(result.stdout.strip()) > 0
            return {
                "running": is_running,
                "pids": result.stdout.strip().split("\n") if is_running else [],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "running": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def read_logs_safely(self) -> List[Dict]:
        """Read logs without interfering with orchestrator writes"""
        logs = []
        if not os.path.exists(self.log_file):
            return logs

        try:
            with open(self.log_file, "r") as f:
                content = f.read().strip()
                if not content:
                    return logs

                # Handle multiple JSON objects on separate lines
                for line in content.split("\n"):
                    line = line.strip()
                    if line and line.startswith("{"):
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"⚠️ Error reading logs: {e}")

        return logs

    def analyze_recent_activity(self, logs: List[Dict]) -> Dict:
        """Analyze recent orchestrator activity"""
        if not logs:
            return {
                "status": "no_logs",
                "message": "No logs available",
                "latest_task": "No tasks found",
                "latest_timestamp": "No timestamp",
                "recent_api_errors": 0,
                "recent_timeouts": 0,
                "recent_successes": 0,
                "total_recent_logs": 0,
                "error_rate": 0,
            }

        recent_logs = logs[-5:]  # Last 5 entries

        # Count error patterns
        api_errors = sum(1 for log in recent_logs if "grok_error" in log)
        timeouts = sum(
            1
            for log in recent_logs
            if "DEADLINE_EXCEEDED" in str(log.get("grok_sdk_error", ""))
        )
        successes = sum(1 for log in recent_logs if log.get("status") == "completed")

        # Get latest task
        latest_task = (
            recent_logs[-1].get("task", "Unknown") if recent_logs else "No tasks"
        )
        latest_timestamp = (
            recent_logs[-1].get("timestamp", "Unknown")
            if recent_logs
            else "No timestamp"
        )

        return {
            "latest_task": latest_task,
            "latest_timestamp": latest_timestamp,
            "recent_api_errors": api_errors,
            "recent_timeouts": timeouts,
            "recent_successes": successes,
            "total_recent_logs": len(recent_logs),
            "error_rate": (
                (api_errors + timeouts) / len(recent_logs) * 100 if recent_logs else 0
            ),
        }

    def check_git_activity(self) -> Dict:
        """Check recent git activity in both repos"""
        activity = {}

        for repo_name, repo_path in [
            ("appia-dev", "/workspaces/appia-dev"),
            ("appIA", "/workspaces/appia-dev/appIA"),
        ]:
            try:
                os.chdir(repo_path)

                # Get last commit info
                result = subprocess.run(
                    ["git", "log", "-1", "--pretty=format:%H|%s|%ar"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout:
                    parts = result.stdout.split("|")
                    activity[repo_name] = {
                        "last_commit_hash": (
                            parts[0][:8] if len(parts) > 0 else "unknown"
                        ),
                        "last_commit_message": (
                            parts[1] if len(parts) > 1 else "unknown"
                        ),
                        "last_commit_time": parts[2] if len(parts) > 2 else "unknown",
                    }
                else:
                    activity[repo_name] = {"error": "Could not get git info"}

            except Exception as e:
                activity[repo_name] = {"error": str(e)}

        # Return to workspace directory
        os.chdir(self.workspace_dir)
        return activity

    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        report = []
        report.append("🤖 JARVYS Orchestrator Monitor Report")
        report.append("=" * 50)
        report.append(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Orchestrator status
        status = self.get_orchestrator_status()
        if status["running"]:
            report.append("✅ Orchestrator Status: RUNNING")
            report.append(f"📍 Process IDs: {', '.join(status['pids'])}")
        else:
            report.append("💤 Orchestrator Status: SLEEPING/STOPPED")
        report.append("")

        # Log analysis
        logs = self.read_logs_safely()
        analysis = self.analyze_recent_activity(logs)

        report.append("📊 Recent Activity Analysis:")
        report.append(f"   📋 Latest Task: {analysis['latest_task']}")
        report.append(f"   🕒 Latest Timestamp: {analysis['latest_timestamp']}")
        report.append(
            f"   ❌ API Errors: {analysis['recent_api_errors']}/5 recent logs"
        )
        report.append(f"   ⏱️ Timeouts: {analysis['recent_timeouts']}/5 recent logs")
        report.append(f"   ✅ Successes: {analysis['recent_successes']}/5 recent logs")
        report.append(f"   📈 Error Rate: {analysis['error_rate']:.1f}%")
        report.append("")

        # Git activity
        git_activity = self.check_git_activity()
        report.append("🔄 Repository Activity:")
        for repo, info in git_activity.items():
            if "error" not in info:
                report.append(f"   📦 {repo}:")
                report.append(f"      🆔 {info['last_commit_hash']}")
                report.append(f"      💬 {info['last_commit_message'][:50]}...")
                report.append(f"      🕐 {info['last_commit_time']}")
            else:
                report.append(f"   ❌ {repo}: {info['error']}")

        return "\n".join(report)

    def monitor_loop(self, interval: int = 300):  # 5 minutes default
        """Main monitoring loop"""
        print("👁️ Starting non-intrusive orchestrator monitoring...")
        print(f"📍 Monitoring interval: {interval} seconds")
        print("🔄 Press Ctrl+C to stop")
        print("")

        try:
            while self.monitoring:
                report = self.generate_status_report()

                # Clear screen and show report
                os.system("clear" if os.name == "posix" else "cls")
                print(report)
                print("")
                print(f"🔄 Next update in {interval} seconds... (Ctrl+C to stop)")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")


if __name__ == "__main__":
    monitor = OrchestrationMonitor()
    monitor.monitor_loop()
