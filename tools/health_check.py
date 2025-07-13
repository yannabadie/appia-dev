"""System health monitoring for JARVYS ecosystem."""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


class JarvysHealthChecker:
    """Health checker for JARVYS ecosystem components."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.check_timestamp = datetime.now()

    def check_environment_health(self) -> Dict[str, Any]:
        """Check environment health status."""
        health = {
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        # Python version check
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if sys.version_info.major == 3 and sys.version_info.minor >= 12:
            health["checks"]["python_version"] = {
                "status": "ok",
                "value": python_version,
            }
        else:
            health["checks"]["python_version"] = {
                "status": "warning",
                "value": python_version,
            }
            health["warnings"].append("Python version should be 3.12+")
            health["status"] = "warning"

        # Required directories check
        required_dirs = ["src", "tests", ".github", "supabase"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                health["checks"][f"dir_{dir_name}"] = {
                    "status": "ok",
                    "exists": True,
                }
            else:
                health["checks"][f"dir_{dir_name}"] = {
                    "status": "error",
                    "exists": False,
                }
                health["errors"].append(f"Missing directory: {dir_name}")
                health["status"] = "unhealthy"

        # Configuration files check
        config_files = [
            "pyproject.toml",
            "pytest.ini",
            ".pre-commit-config.yaml",
        ]
        for file_name in config_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                health["checks"][f"config_{file_name}"] = {
                    "status": "ok",
                    "exists": True,
                }
            else:
                health["checks"][f"config_{file_name}"] = {
                    "status": "warning",
                    "exists": False,
                }
                health["warnings"].append(f"Missing configuration file: {file_name}")
                if health["status"] == "healthy":
                    health["status"] = "warning"

        return health

    def check_dependencies_health(self) -> Dict[str, Any]:
        """Check Python dependencies health."""
        health = {
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        # Core dependencies
        core_deps = [
            ("openai", "OpenAI API client"),
            ("supabase", "Supabase client"),
            ("fastapi", "FastAPI framework"),
            ("github", "PyGithub library"),
            ("pytest", "Testing framework"),
        ]

        for dep_name, description in core_deps:
            try:
                module = __import__(dep_name)
                version = getattr(module, "__version__", "unknown")
                health["checks"][dep_name] = {
                    "status": "ok",
                    "installed": True,
                    "version": version,
                    "description": description,
                }
            except ImportError:
                health["checks"][dep_name] = {
                    "status": "error",
                    "installed": False,
                    "description": description,
                }
                health["errors"].append(f"Missing dependency: {dep_name}")
                health["status"] = "unhealthy"

        return health

    def check_api_health(self) -> Dict[str, Any]:
        """Check external API health."""
        health = {
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        # OpenAI API
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=openai_key)

                start_time = time.time()
                models = client.models.list()
                response_time = time.time() - start_time

                health["checks"]["openai_api"] = {
                    "status": "ok",
                    "response_time": round(response_time, 3),
                    "models_count": len(models.data),
                }
            except Exception as e:
                health["checks"]["openai_api"] = {
                    "status": "error",
                    "error": str(e)[:100],
                }
                health["errors"].append("OpenAI API connection failed")
                health["status"] = "unhealthy"
        else:
            health["checks"]["openai_api"] = {
                "status": "warning",
                "error": "API key not configured",
            }
            health["warnings"].append("OpenAI API key not configured")
            if health["status"] == "healthy":
                health["status"] = "warning"

        # Supabase API
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                from supabase import create_client

                client = create_client(supabase_url, supabase_key)

                start_time = time.time()
                response = client.table("health_check").select("*").limit(1).execute()
                response_time = time.time() - start_time

                health["checks"]["supabase_api"] = {
                    "status": "ok",
                    "response_time": round(response_time, 3),
                    "url": supabase_url[:50] + "...",
                }
            except Exception as e:
                error_str = str(e).lower()
                if "relation" in error_str and "does not exist" in error_str:
                    health["checks"]["supabase_api"] = {
                        "status": "ok",
                        "note": "Connected (health_check table doesn't exist - normal)",
                    }
                else:
                    health["checks"]["supabase_api"] = {
                        "status": "error",
                        "error": str(e)[:100],
                    }
                    health["errors"].append("Supabase API connection failed")
                    health["status"] = "unhealthy"
        else:
            health["checks"]["supabase_api"] = {
                "status": "warning",
                "error": "Credentials not configured",
            }
            health["warnings"].append("Supabase credentials not configured")
            if health["status"] == "healthy":
                health["status"] = "warning"

        # GitHub API
        github_token = os.getenv("GH_TOKEN")
        if github_token:
            try:
                from github import Github

                client = Github(github_token)

                start_time = time.time()
                user = client.get_user()
                rate_limit = client.get_rate_limit()
                response_time = time.time() - start_time

                health["checks"]["github_api"] = {
                    "status": "ok",
                    "response_time": round(response_time, 3),
                    "rate_limit_remaining": rate_limit.core.remaining,
                    "user": user.login,
                }

                # Warn if rate limit is low
                if rate_limit.core.remaining < 100:
                    health["warnings"].append(
                        f"GitHub rate limit low: {rate_limit.core.remaining}"
                    )
                    if health["status"] == "healthy":
                        health["status"] = "warning"

            except Exception as e:
                health["checks"]["github_api"] = {
                    "status": "error",
                    "error": str(e)[:100],
                }
                health["errors"].append("GitHub API connection failed")
                health["status"] = "unhealthy"
        else:
            health["checks"]["github_api"] = {
                "status": "warning",
                "error": "Token not configured",
            }
            health["warnings"].append("GitHub token not configured")
            if health["status"] == "healthy":
                health["status"] = "warning"

        return health

    def check_services_health(self) -> Dict[str, Any]:
        """Check local services health."""
        health = {
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        # FastAPI app health
        try:
            app_file = self.project_root / "app" / "main.py"
            if app_file.exists():
                # Try to import the app
                sys.path.insert(0, str(self.project_root))
                try:
                    from app.main import app

                    health["checks"]["fastapi_app"] = {
                        "status": "ok",
                        "importable": True,
                        "routes": len(app.routes),
                    }
                except ImportError as e:
                    health["checks"]["fastapi_app"] = {
                        "status": "warning",
                        "importable": False,
                        "error": str(e)[:100],
                    }
                    health["warnings"].append("FastAPI app not importable")
                    if health["status"] == "healthy":
                        health["status"] = "warning"
                finally:
                    if str(self.project_root) in sys.path:
                        sys.path.remove(str(self.project_root))
            else:
                health["checks"]["fastapi_app"] = {
                    "status": "warning",
                    "exists": False,
                }
                health["warnings"].append("FastAPI app file not found")
                if health["status"] == "healthy":
                    health["status"] = "warning"
        except Exception as e:
            health["checks"]["fastapi_app"] = {
                "status": "error",
                "error": str(e)[:100],
            }
            health["errors"].append("FastAPI app check failed")
            health["status"] = "unhealthy"

        # Database health
        metrics_db = self.project_root / "jarvys_metrics.db"
        if metrics_db.exists():
            try:
                size_mb = metrics_db.stat().st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(metrics_db.stat().st_mtime)
                age_hours = (datetime.now() - modified).total_seconds() / 3600

                health["checks"]["metrics_database"] = {
                    "status": "ok",
                    "exists": True,
                    "size_mb": round(size_mb, 2),
                    "age_hours": round(age_hours, 1),
                }

                # Warn if database is old
                if age_hours > 24:
                    health["warnings"].append(
                        f"Metrics database is {age_hours:.1f} hours old"
                    )
                    if health["status"] == "healthy":
                        health["status"] = "warning"

            except Exception as e:
                health["checks"]["metrics_database"] = {
                    "status": "error",
                    "error": str(e)[:100],
                }
                health["errors"].append("Metrics database check failed")
                health["status"] = "unhealthy"
        else:
            health["checks"]["metrics_database"] = {
                "status": "info",
                "exists": False,
                "note": "Not created yet",
            }

        return health

    def check_workflows_health(self) -> Dict[str, Any]:
        """Check GitHub workflows health."""
        health = {
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": [],
        }

        workflows_dir = self.project_root / ".github" / "workflows"
        if not workflows_dir.exists():
            health["checks"]["workflows_directory"] = {
                "status": "error",
                "exists": False,
            }
            health["errors"].append("Workflows directory not found")
            health["status"] = "unhealthy"
            return health

        # Check workflow files
        workflow_files = list(workflows_dir.glob("*.yml"))
        health["checks"]["workflows_directory"] = {
            "status": "ok",
            "exists": True,
            "count": len(workflow_files),
        }

        # Required workflows
        required_workflows = ["ci.yml", "agent.yml"]
        for workflow_name in required_workflows:
            workflow_path = workflows_dir / workflow_name
            if workflow_path.exists():
                try:
                    import yaml

                    with open(workflow_path) as f:
                        workflow_config = yaml.safe_load(f)

                    health["checks"][f"workflow_{workflow_name}"] = {
                        "status": "ok",
                        "exists": True,
                        "jobs": len(workflow_config.get("jobs", {})),
                        "triggers": list(workflow_config.get("on", {}).keys()),
                    }
                except Exception as e:
                    health["checks"][f"workflow_{workflow_name}"] = {
                        "status": "error",
                        "exists": True,
                        "error": str(e)[:100],
                    }
                    health["errors"].append(
                        f"Workflow {workflow_name} has syntax errors"
                    )
                    health["status"] = "unhealthy"
            else:
                health["checks"][f"workflow_{workflow_name}"] = {
                    "status": "warning",
                    "exists": False,
                }
                health["warnings"].append(
                    f"Required workflow {workflow_name} not found"
                )
                if health["status"] == "healthy":
                    health["status"] = "warning"

        return health

    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check."""
        overall_health = {
            "timestamp": self.check_timestamp.isoformat(),
            "overall_status": "healthy",
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "warnings": 0,
                "errors": 0,
            },
            "components": {},
        }

        # Run all health checks
        components = {
            "environment": self.check_environment_health,
            "dependencies": self.check_dependencies_health,
            "apis": self.check_api_health,
            "services": self.check_services_health,
            "workflows": self.check_workflows_health,
        }

        overall_warnings = []
        overall_errors = []

        for component_name, check_function in components.items():
            component_health = check_function()
            overall_health["components"][component_name] = component_health

            # Count checks
            overall_health["summary"]["total_checks"] += len(
                component_health.get("checks", {})
            )

            # Aggregate status
            if component_health["status"] == "unhealthy":
                overall_health["overall_status"] = "unhealthy"
                overall_errors.extend(component_health.get("errors", []))
            elif (
                component_health["status"] == "warning"
                and overall_health["overall_status"] != "unhealthy"
            ):
                overall_health["overall_status"] = "warning"
                overall_warnings.extend(component_health.get("warnings", []))

            # Count passed/warning/error checks
            for check_name, check_result in component_health.get("checks", {}).items():
                if check_result["status"] == "ok":
                    overall_health["summary"]["passed"] += 1
                elif check_result["status"] == "warning":
                    overall_health["summary"]["warnings"] += 1
                elif check_result["status"] == "error":
                    overall_health["summary"]["errors"] += 1

        overall_health["warnings"] = overall_warnings
        overall_health["errors"] = overall_errors

        return overall_health

    def save_health_report(self, output_file: Optional[str] = None) -> str:
        """Save health check report to file."""
        health_report = self.run_comprehensive_health_check()

        if output_file:
            output_path = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.project_root / f"health_report_{timestamp}.json"

        with open(output_path, "w") as f:
            json.dump(health_report, f, indent=2, default=str)

        return str(output_path)

    def print_health_summary(self):
        """Print a human-readable health summary."""
        health = self.run_comprehensive_health_check()

        print("🏥 JARVYS Health Check Summary")
        print("=" * 50)
        print(f"Overall Status: {health['overall_status'].upper()}")
        print(f"Timestamp: {health['timestamp']}")
        print()

        summary = health["summary"]
        print(f"📊 Summary:")
        print(f"  Total Checks: {summary['total_checks']}")
        print(f"  ✅ Passed: {summary['passed']}")
        print(f"  ⚠️  Warnings: {summary['warnings']}")
        print(f"  ❌ Errors: {summary['errors']}")
        print()

        # Show component status
        print("🔧 Component Status:")
        for component_name, component_health in health["components"].items():
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "unhealthy": "❌",
            }.get(component_health["status"], "❓")

            print(
                f"  {status_emoji} {component_name.title()}: {component_health['status']}"
            )

        # Show warnings if any
        if health["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in health["warnings"]:
                print(f"  - {warning}")

        # Show errors if any
        if health["errors"]:
            print("\n❌ Errors:")
            for error in health["errors"]:
                print(f"  - {error}")

        print()


def main():
    """Main entry point for health checker."""
    checker = JarvysHealthChecker()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "report":
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            report_path = checker.save_health_report(output_file)
            print(f"Health report saved to: {report_path}")

        elif command == "json":
            health = checker.run_comprehensive_health_check()
            print(json.dumps(health, indent=2, default=str))

        elif command == "summary" or command == "check":
            checker.print_health_summary()

        else:
            print(f"Unknown command: {command}")
            print(
                "Usage: python health_check.py [report|json|summary|check] [output_file]"
            )
    else:
        checker.print_health_summary()


if __name__ == "__main__":
    main()
