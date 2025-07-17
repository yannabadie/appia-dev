#!/usr/bin/env python3
"""
JARVYS Orchestrator Monitor - 20 Minutes Surveillance
Monitor real-time execution with bug detection and anomaly alerts
"""

import subprocess
import threading
import time
from datetime import datetime, timedelta

from grok_orchestrator import (
    get_available_secrets_summary,
    supabase,
    validate_claude_api,
    validate_grok_api,
)


class JarvysMonitor:
    def __init__(self, duration_minutes=20):
        self.duration_minutes = duration_minutes
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.monitoring = True
        self.alerts = []
        self.stats = {
            "cycles_completed": 0,
            "errors_detected": 0,
            "api_calls": {"grok": 0, "claude": 0},
            "memory_operations": 0,
            "performance_issues": 0,
        }

    def log_alert(self, level, message, details=None):
        """Log monitoring alerts with timestamp"""
        alert = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message,
            "details": details or {},
        }
        self.alerts.append(alert)

        # Print color-coded alerts
        colors = {
            "🔴 CRITICAL": "\033[91m",
            "🟡 WARNING": "\033[93m",
            "🔵 INFO": "\033[94m",
            "🟢 SUCCESS": "\033[92m",
        }
        reset = "\033[0m"

        color = colors.get(level, "")
        print(f"{color}[{alert['timestamp']}] {level}: {message}{reset}")

        if details:
            print(f"  📋 Details: {details}")

    def check_system_health(self):
        """Check system health indicators"""
        health_issues = []

        # Check APIs
        if not validate_grok_api():
            health_issues.append("Grok API unreachable")
        if not validate_claude_api():
            health_issues.append("Claude API unreachable")

        # Check Supabase connection
        if supabase:
            try:
                supabase.table("jarvys_memory").select("*").limit(1).execute()
            except Exception as e:
                health_issues.append(f"Supabase connection failed: {str(e)}")
        else:
            health_issues.append("Supabase not initialized")

        # Check secrets
        secrets = get_available_secrets_summary()
        missing_secrets = [
            k
            for k, v in secrets.items()
            if not v and k in ["xai_grok", "claude", "github", "supabase"]
        ]
        if missing_secrets:
            health_issues.append(f"Missing critical secrets: {missing_secrets}")

        return health_issues

    def monitor_orchestrator_process(self, process):
        """Monitor the orchestrator process for issues"""
        output_buffer = []
        error_patterns = [
            "ERROR",
            "FAILED",
            "Exception",
            "Traceback",
            "timeout",
            "DEADLINE_EXCEEDED",
            "rate limit",
            "authentication",
            "permission denied",
            "connection refused",
        ]

        warning_patterns = [
            "WARNING",
            "retry",
            "fallback",
            "degraded",
            "slow response",
            "high latency",
            "memory usage",
        ]

        while self.monitoring and process.poll() is None:
            try:
                # Read output
                output = process.stdout.readline()
                if output:
                    line = output.decode("utf-8").strip()
                    output_buffer.append(line)

                    # Keep only last 50 lines
                    if len(output_buffer) > 50:
                        output_buffer.pop(0)

                    # Check for error patterns
                    line_lower = line.lower()
                    for pattern in error_patterns:
                        if pattern.lower() in line_lower:
                            self.log_alert(
                                "🔴 CRITICAL",
                                f"Error detected: {pattern}",
                                {"line": line},
                            )
                            self.stats["errors_detected"] += 1
                            break

                    # Check for warning patterns
                    for pattern in warning_patterns:
                        if pattern.lower() in line_lower:
                            self.log_alert(
                                "🟡 WARNING",
                                f"Warning detected: {pattern}",
                                {"line": line},
                            )
                            break

                    # Track API calls
                    if "grok" in line_lower and (
                        "api" in line_lower or "query" in line_lower
                    ):
                        self.stats["api_calls"]["grok"] += 1
                    if "claude" in line_lower and (
                        "api" in line_lower or "validat" in line_lower
                    ):
                        self.stats["api_calls"]["claude"] += 1

                    # Track memory operations
                    if "memory stored" in line_lower or "🧠" in line:
                        self.stats["memory_operations"] += 1

                    # Track cycle completion
                    if "cycle" in line_lower and (
                        "completed" in line_lower or "success" in line_lower
                    ):
                        self.stats["cycles_completed"] += 1
                        self.log_alert(
                            "🟢 SUCCESS",
                            f"Cycle completed: {self.stats['cycles_completed']}",
                        )

                time.sleep(0.1)  # Small delay to prevent CPU overload

            except Exception as e:
                self.log_alert("🟡 WARNING", f"Monitor read error: {str(e)}")
                time.sleep(1)

        return output_buffer

    def health_check_loop(self):
        """Periodic health checks every 2 minutes"""
        while self.monitoring:
            time.sleep(120)  # Check every 2 minutes

            if not self.monitoring:
                break

            self.log_alert("🔵 INFO", "Performing periodic health check...")

            health_issues = self.check_system_health()
            if health_issues:
                self.log_alert(
                    "🔴 CRITICAL", "Health check failed", {"issues": health_issues}
                )
            else:
                self.log_alert("🟢 SUCCESS", "Health check passed")

            # Performance check
            runtime = datetime.now() - self.start_time
            if (
                self.stats["cycles_completed"] == 0 and runtime.total_seconds() > 300
            ):  # 5 min no cycles
                self.log_alert("🟡 WARNING", "No cycles completed after 5 minutes")
                self.stats["performance_issues"] += 1

    def generate_report(self):
        """Generate final monitoring report"""
        runtime = datetime.now() - self.start_time

        report = {
            "monitoring_summary": {
                "start_time": self.start_time.strftime("%H:%M:%S"),
                "end_time": datetime.now().strftime("%H:%M:%S"),
                "duration_minutes": round(runtime.total_seconds() / 60, 1),
                "total_alerts": len(self.alerts),
            },
            "performance_stats": self.stats,
            "alert_breakdown": {
                "critical": len(
                    [a for a in self.alerts if a["level"] == "🔴 CRITICAL"]
                ),
                "warnings": len([a for a in self.alerts if a["level"] == "🟡 WARNING"]),
                "info": len([a for a in self.alerts if a["level"] == "🔵 INFO"]),
                "success": len([a for a in self.alerts if a["level"] == "🟢 SUCCESS"]),
            },
            "recent_alerts": self.alerts[-10:] if self.alerts else [],  # Last 10 alerts
        }

        return report


def main():
    print("🚀 JARVYS ORCHESTRATOR - 20 MINUTE MONITORED EXECUTION")
    print("=" * 70)
    print(f"⏰ Start Time: {datetime.now().strftime('%H:%M:%S')}")
    print(
        f"⏰ End Time: {(datetime.now() + timedelta(minutes=20)).strftime('%H:%M:%S')}"
    )
    print("🔍 Real-time monitoring active for bugs and anomalies...")
    print("=" * 70)

    # Initialize monitor
    monitor = JarvysMonitor(duration_minutes=20)

    # Initial health check
    monitor.log_alert("🔵 INFO", "Performing initial system health check...")
    health_issues = monitor.check_system_health()

    if health_issues:
        monitor.log_alert(
            "🔴 CRITICAL", "Initial health check failed", {"issues": health_issues}
        )
        print("❌ Critical issues detected. Aborting orchestrator launch.")
        return
    else:
        monitor.log_alert(
            "🟢 SUCCESS", "Initial health check passed - All systems operational"
        )

    # Start health monitoring thread
    health_thread = threading.Thread(target=monitor.health_check_loop, daemon=True)
    health_thread.start()

    try:
        # Launch orchestrator process
        monitor.log_alert("🔵 INFO", "Launching JARVYS orchestrator...")

        # Use timeout to limit execution to 20 minutes (1200 seconds)
        cmd = ["timeout", "1200s", "python", "grok_orchestrator.py"]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd="/workspaces/appia-dev",
        )

        monitor.log_alert(
            "🟢 SUCCESS", f"Orchestrator launched with PID: {process.pid}"
        )

        # Monitor the process
        output_buffer = monitor.monitor_orchestrator_process(process)

        # Wait for process completion or timeout
        try:
            process.wait(timeout=1200)  # 20 minutes max
            monitor.log_alert("🔵 INFO", "Orchestrator process completed normally")
        except subprocess.TimeoutExpired:
            monitor.log_alert(
                "🟡 WARNING", "20-minute timeout reached, terminating orchestrator"
            )
            process.terminate()

    except KeyboardInterrupt:
        monitor.log_alert("🟡 WARNING", "Monitoring interrupted by user")
        if "process" in locals():
            process.terminate()
    except Exception as e:
        monitor.log_alert("🔴 CRITICAL", f"Monitor execution failed: {str(e)}")
    finally:
        monitor.monitoring = False

        # Generate final report
        print("\n" + "=" * 70)
        print("📊 FINAL MONITORING REPORT")
        print("=" * 70)

        report = monitor.generate_report()

        print(
            f"⏱️ Execution Duration: {report['monitoring_summary']['duration_minutes']} minutes"
        )
        print(f"🔄 Cycles Completed: {report['performance_stats']['cycles_completed']}")
        print(f"❌ Errors Detected: {report['performance_stats']['errors_detected']}")
        print(
            f"🔥 Performance Issues: {report['performance_stats']['performance_issues']}"
        )
        print(
            f"📞 API Calls - Grok: {report['performance_stats']['api_calls']['grok']}, Claude: {report['performance_stats']['api_calls']['claude']}"
        )
        print(
            f"🧠 Memory Operations: {report['performance_stats']['memory_operations']}"
        )
        print(f"🚨 Total Alerts: {report['monitoring_summary']['total_alerts']}")
        print(f"   Critical: {report['alert_breakdown']['critical']}")
        print(f"   Warnings: {report['alert_breakdown']['warnings']}")
        print(f"   Info: {report['alert_breakdown']['info']}")
        print(f"   Success: {report['alert_breakdown']['success']}")

        if report["recent_alerts"]:
            print("\n🔍 RECENT ALERTS:")
            for alert in report["recent_alerts"]:
                print(f"  [{alert['timestamp']}] {alert['level']}: {alert['message']}")

        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        if report["performance_stats"]["errors_detected"] == 0:
            print("✅ EXCELLENT: No critical errors detected")
        elif report["performance_stats"]["errors_detected"] < 3:
            print("⚠️ GOOD: Minor issues detected but manageable")
        else:
            print("❌ ATTENTION REQUIRED: Multiple errors detected")

        print("\n🏁 Monitoring completed successfully!")


if __name__ == "__main__":
    main()
