"""Interactive debugging interface for JARVYS ecosystem."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class JarvysDebugDashboard:
    """Interactive debugging dashboard for JARVYS ecosystem."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.session_start = datetime.now()
        self.debug_log = []

    def log_debug(self, message: str, level: str = "INFO"):
        """Log debug message with timestamp."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
        }
        self.debug_log.append(entry)
        print(f"[{level}] {message}")

    def check_environment(self) -> Dict[str, Any]:
        """Check environment configuration."""
        self.log_debug("Checking environment configuration...")

        env_status = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "project_root": str(self.project_root),
            "environment_vars": {},
            "required_files": {},
            "dependencies": {},
        }

        # Check environment variables
        required_vars = [
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "GITHUB_TOKEN",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY",
        ]

        for var in required_vars:
            value = os.getenv(var)
            env_status["environment_vars"][var] = {
                "present": value is not None,
                "length": len(value) if value else 0,
                "prefix": (value[:10] + "..." if value and len(value) > 10 else value),
            }

        # Check required files
        required_files = [
            "pyproject.toml",
            "README.md",
            ".github/workflows/ci.yml",
            "src/jarvys_dev/main.py",
            "supabase/config.toml",
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            env_status["required_files"][file_path] = {
                "exists": full_path.exists(),
                "size": full_path.stat().st_size if full_path.exists() else 0,
            }

        # Check Python dependencies
        try:
            import openai

            env_status["dependencies"]["openai"] = {
                "installed": True,
                "version": getattr(openai, "__version__", "unknown"),
            }
        except ImportError:
            env_status["dependencies"]["openai"] = {"installed": False}

        try:
            import supabase

            env_status["dependencies"]["supabase"] = {
                "installed": True,
                "version": getattr(supabase, "__version__", "unknown"),
            }
        except ImportError:
            env_status["dependencies"]["supabase"] = {"installed": False}

        try:
            import github

            env_status["dependencies"]["github"] = {
                "installed": True,
                "version": getattr(github, "__version__", "unknown"),
            }
        except ImportError:
            env_status["dependencies"]["github"] = {"installed": False}

        return env_status

    def test_connectivity(self) -> Dict[str, Any]:
        """Test connectivity to external services."""
        self.log_debug("Testing connectivity to external services...")

        connectivity_status = {
            "openai": {"status": "unknown", "details": ""},
            "supabase": {"status": "unknown", "details": ""},
            "github": {"status": "unknown", "details": ""},
            "gemini": {"status": "unknown", "details": ""},
            "anthropic": {"status": "unknown", "details": ""},
        }

        # Test OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                # Initialize client properly
                import openai

                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                models = client.models.list()
                connectivity_status["openai"] = {
                    "status": "connected",
                    "details": f"Found {len(models.data)} models",
                }
            except Exception as e:
                connectivity_status["openai"] = {
                    "status": "error",
                    "details": str(e)[:100],
                }
        else:
            connectivity_status["openai"] = {
                "status": "no_key",
                "details": "OPENAI_API_KEY not set",
            }

        # Test Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                from supabase import create_client

                client = create_client(supabase_url, supabase_key)
                # Try a simple operation
                client.table("test_table").select("*").limit(1).execute()
                connectivity_status["supabase"] = {
                    "status": "connected",
                    "details": "Connection successful",
                }
            except Exception as e:
                error_str = str(e).lower()
                if "relation" in error_str and "does not exist" in error_str:
                    connectivity_status["supabase"] = {
                        "status": "connected",
                        "details": "Connected (test table doesn't exist - normal)",
                    }
                else:
                    connectivity_status["supabase"] = {
                        "status": "error",
                        "details": str(e)[:100],
                    }
        else:
            connectivity_status["supabase"] = {
                "status": "no_credentials",
                "details": "Supabase credentials not set",
            }

        # Test GitHub
        github_token = os.getenv("GH_TOKEN")
        if github_token:
            try:
                from github import Github

                _client = Github(github_token)
                user = client.get_user()
                rate_limit = client.get_rate_limit()
                connectivity_status["github"] = {
                    "status": "connected",
                    "details": f"User: {user.login}, Rate limit: {rate_limit.core.remaining}",
                }
            except Exception as e:
                connectivity_status["github"] = {
                    "status": "error",
                    "details": str(e)[:100],
                }
        else:
            connectivity_status["github"] = {
                "status": "no_token",
                "details": "GITHUB_TOKEN not set",
            }

        return connectivity_status

    def check_workflows(self) -> Dict[str, Any]:
        """Check GitHub Actions workflows status."""
        self.log_debug("Checking GitHub Actions workflows...")

        workflows_path = self.project_root / ".github" / "workflows"
        workflow_status = {
            "directory_exists": workflows_path.exists(),
            "workflows": {},
            "total_workflows": 0,
            "valid_workflows": 0,
        }

        if workflows_path.exists():
            workflow_files = list(workflows_path.glob("*.yml"))
            workflow_status["total_workflows"] = len(workflow_files)

            for workflow_file in workflow_files:
                try:
                    import yaml

                    with open(workflow_file) as f:
                        workflow_config = yaml.safe_load(f)

                    workflow_status["workflows"][workflow_file.name] = {
                        "valid": True,
                        "name": workflow_config.get("name", "Unnamed"),
                        "triggers": list(workflow_config.get("on", {}).keys()),
                        "jobs": len(workflow_config.get("jobs", {})),
                    }
                    workflow_status["valid_workflows"] += 1

                except Exception as e:
                    workflow_status["workflows"][workflow_file.name] = {
                        "valid": False,
                        "error": str(e)[:100],
                    }

        return workflow_status

    def analyze_logs(self) -> Dict[str, Any]:
        """Analyze system logs and metrics."""
        self.log_debug("Analyzing system logs and metrics...")

        log_analysis = {
            "metrics_db": {"exists": False, "size": 0, "records": 0},
            "log_files": [],
            "recent_activity": [],
        }

        # Check metrics database
        metrics_db = self.project_root / "jarvys_metrics.db"
        if metrics_db.exists():
            log_analysis["metrics_db"] = {
                "exists": True,
                "size": metrics_db.stat().st_size,
                "records": "unknown",  # Would need SQLite to count
            }

        # Look for log files
        log_patterns = ["*.log", "*.out", "*.err"]
        for pattern in log_patterns:
            log_files = list(self.project_root.rglob(pattern))
            for log_file in log_files[:10]:  # Limit to avoid too many files
                log_analysis["log_files"].append(
                    {
                        "path": str(log_file.relative_to(self.project_root)),
                        "size": log_file.stat().st_size,
                        "modified": log_file.stat().st_mtime,
                    }
                )

        return log_analysis

    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics."""
        self.log_debug("Running comprehensive diagnostics...")

        diagnostics = {
            "session_info": {
                "start_time": self.session_start.isoformat(),
                "duration_seconds": (
                    datetime.now() - self.session_start
                ).total_seconds(),
            },
            "environment": self.check_environment(),
            "connectivity": self.test_connectivity(),
            "workflows": self.check_workflows(),
            "logs": self.analyze_logs(),
            "debug_log": self.debug_log,
        }

        return diagnostics

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate diagnostic report."""
        diagnostics = self.run_diagnostics()

        if output_file:
            output_path = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.project_root / f"debug_report_{timestamp}.json"

        with open(output_path, "w") as f:
            json.dump(diagnostics, f, indent=2, default=str)

        self.log_debug(f"Debug report saved to: {output_path}")
        return str(output_path)

    def interactive_mode(self):
        """Run interactive debugging mode."""
        print("🔧 JARVYS Debug Dashboard")
        print("=" * 50)

        while True:
            print("\nAvailable commands:")
            print("1. Check environment")
            print("2. Test connectivity")
            print("3. Check workflows")
            print("4. Analyze logs")
            print("5. Run full diagnostics")
            print("6. Generate report")
            print("7. Exit")

            try:
                choice = input("\nEnter your choice (1-7): ").strip()

                if choice == "1":
                    env_status = self.check_environment()
                    print(json.dumps(env_status, indent=2))

                elif choice == "2":
                    connectivity = self.test_connectivity()
                    print(json.dumps(connectivity, indent=2))

                elif choice == "3":
                    workflows = self.check_workflows()
                    print(json.dumps(workflows, indent=2))

                elif choice == "4":
                    logs = self.analyze_logs()
                    print(json.dumps(logs, indent=2))

                elif choice == "5":
                    diagnostics = self.run_diagnostics()
                    print(json.dumps(diagnostics, indent=2))

                elif choice == "6":
                    report_path = self.generate_report()
                    print(f"Report generated: {report_path}")

                elif choice == "7":
                    print("Exiting debug dashboard...")
                    break

                else:

            except KeyboardInterrupt:
                print("\nExiting debug dashboard...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point for debug dashboard."""
    dashboard = JarvysDebugDashboard()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "report":
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            report_path = dashboard.generate_report(output_file)
            print(f"Debug report generated: {report_path}")

        elif command == "check":
            diagnostics = dashboard.run_diagnostics()
            print(json.dumps(diagnostics, indent=2))

        else:
            print(f"Unknown command: {command}")
            print("Usage: python debug_dashboard.py [report|check] [output_file]")
    else:
        dashboard.interactive_mode()


if __name__ == "__main__":
    main()
