"""Error detection and reporting for JARVYS ecosystem."""

import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """Error severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ErrorPattern:
    """Error pattern definition."""

    name: str
    pattern: str
    severity: ErrorSeverity
    description: str
    suggested_fix: str


@dataclass
class DetectedError:
    """Detected error instance."""

    pattern_name: str
    severity: ErrorSeverity
    message: str
    location: str
    timestamp: datetime
    context: List[str]
    suggested_fix: str

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["severity"] = self.severity.value
        data["timestamp"] = self.timestamp.isoformat()
        return data


class JarvysErrorTracker:
    """Error detection and tracking system for JARVYS ecosystem."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scan_timestamp = datetime.now()
        self.detected_errors = []
        self.error_patterns = self._initialize_error_patterns()

    def _initialize_error_patterns(self) -> List[ErrorPattern]:
        """Initialize error patterns to detect."""
        patterns = [
            # API and Authentication Errors
            ErrorPattern(
                name="openai_auth_error",
                pattern=r"(?i)(unauthorized|invalid.*api.*key|401.*openai|authentication.*failed.*openai)",
                severity=ErrorSeverity.HIGH,
                description="OpenAI API authentication failure",
                suggested_fix="Check OPENAI_API_KEY environment variable",
            ),
            ErrorPattern(
                name="supabase_auth_error",
                pattern=r"(?i)(unauthorized.*supabase|invalid.*supabase.*key|403.*supabase)",
                severity=ErrorSeverity.HIGH,
                description="Supabase authentication failure",
                suggested_fix="Check SUPABASE_URL and SUPABASE_KEY environment variables",
            ),
            ErrorPattern(
                name="github_auth_error",
                pattern=r"(?i)(bad.*credentials.*github|invalid.*github.*token|401.*github)",
                severity=ErrorSeverity.HIGH,
                description="GitHub API authentication failure",
                suggested_fix="Check GITHUB_TOKEN environment variable",
            ),
            # Rate Limiting Errors
            ErrorPattern(
                name="rate_limit_exceeded",
                pattern=r"(?i)(rate.*limit.*exceeded|429|too.*many.*requests)",
                severity=ErrorSeverity.MEDIUM,
                description="API rate limit exceeded",
                suggested_fix="Implement exponential backoff or check API usage",
            ),
            # Network Errors
            ErrorPattern(
                name="connection_error",
                pattern=r"(?i)(connection.*error|network.*error|timeout|connection.*refused)",
                severity=ErrorSeverity.MEDIUM,
                description="Network connectivity issue",
                suggested_fix="Check internet connection and service availability",
            ),
            ErrorPattern(
                name="dns_resolution_error",
                pattern=r"(?i)(name.*resolution.*error|dns.*error|failed.*to.*resolve)",
                severity=ErrorSeverity.MEDIUM,
                description="DNS resolution failure",
                suggested_fix="Check network connectivity and DNS settings",
            ),
            # Configuration Errors
            ErrorPattern(
                name="missing_env_var",
                pattern=r"(?i)(environment.*variable.*not.*set|missing.*env|keyerror.*env)",
                severity=ErrorSeverity.HIGH,
                description="Missing environment variable",
                suggested_fix="Set required environment variables",
            ),
            ErrorPattern(
                name="config_file_missing",
                pattern=r"(?i)(config.*file.*not.*found|no.*such.*file.*config)",
                severity=ErrorSeverity.HIGH,
                description="Configuration file missing",
                suggested_fix="Create required configuration files",
            ),
            # Database Errors
            ErrorPattern(
                name="database_connection_error",
                pattern=r"(?i)(database.*connection.*failed|could.*not.*connect.*database)",
                severity=ErrorSeverity.CRITICAL,
                description="Database connection failure",
                suggested_fix="Check database credentials and connectivity",
            ),
            ErrorPattern(
                name="table_not_found",
                pattern=r"(?i)(table.*does.*not.*exist|relation.*does.*not.*exist)",
                severity=ErrorSeverity.MEDIUM,
                description="Database table missing",
                suggested_fix="Run database migrations or create missing tables",
            ),
            # Import and Dependency Errors
            ErrorPattern(
                name="import_error",
                pattern=r"(?i)(modulenotfounderror|importerror|no.*module.*named)",
                severity=ErrorSeverity.HIGH,
                description="Missing Python module",
                suggested_fix="Install missing dependencies with pip or poetry",
            ),
            ErrorPattern(
                name="version_conflict",
                pattern=r"(?i)(version.*conflict|incompatible.*version|version.*mismatch)",
                severity=ErrorSeverity.MEDIUM,
                description="Dependency version conflict",
                suggested_fix="Update dependencies to compatible versions",
            ),
            # Workflow and CI/CD Errors
            ErrorPattern(
                name="workflow_syntax_error",
                pattern=r"(?i)(workflow.*syntax.*error|invalid.*yaml|yaml.*parse.*error)",
                severity=ErrorSeverity.HIGH,
                description="GitHub workflow syntax error",
                suggested_fix="Check YAML syntax in workflow files",
            ),
            ErrorPattern(
                name="workflow_permission_error",
                pattern=r"(?i)(permission.*denied.*workflow|insufficient.*permissions.*github)",
                severity=ErrorSeverity.HIGH,
                description="Workflow permission error",
                suggested_fix="Check repository permissions and secrets",
            ),
            # Runtime Errors
            ErrorPattern(
                name="memory_error",
                pattern=r"(?i)(out.*of.*memory|memory.*error|memoryerror)",
                severity=ErrorSeverity.CRITICAL,
                description="Memory exhaustion",
                suggested_fix="Optimize memory usage or increase available memory",
            ),
            ErrorPattern(
                name="disk_space_error",
                pattern=r"(?i)(no.*space.*left|disk.*full|out.*of.*disk.*space)",
                severity=ErrorSeverity.CRITICAL,
                description="Disk space exhausted",
                suggested_fix="Free up disk space or increase storage",
            ),
            # Security Errors
            ErrorPattern(
                name="secret_exposed",
                pattern=r"(sk-[a-zA-Z0-9]{48,}|ghp_[a-zA-Z0-9]{36}|eyJ[a-zA-Z0-9+/=]+)",
                severity=ErrorSeverity.CRITICAL,
                description="Potential secret exposure in logs",
                suggested_fix="Remove secrets from logs and rotate exposed credentials",
            ),
            # Performance Issues
            ErrorPattern(
                name="slow_response",
                pattern=r"(?i)(slow.*response|timeout.*exceeded|request.*took.*too.*long)",
                severity=ErrorSeverity.LOW,
                description="Performance issue detected",
                suggested_fix="Optimize performance or increase timeout values",
            ),
        ]

        return patterns

    def scan_file_for_errors(self, file_path: Path) -> List[DetectedError]:
        """Scan a single file for error patterns."""
        errors = []

        try:
            # Skip binary files and large files
            if file_path.stat().st_size > 10 * 1024 * 1024:  # Skip files > 10MB
                return errors

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern in self.error_patterns:
                    if re.search(pattern.pattern, line):
                        # Get context lines
                        context_start = max(0, line_num - 3)
                        context_end = min(len(lines), line_num + 2)
                        context = [
                            f"{i+1}: {lines[i].rstrip()}"
                            for _i in range(context_start, context_end)
                        ]

                        error = DetectedError(
                            pattern_name=pattern.name,
                            severity=pattern.severity,
                            message=pattern.description,
                            location=f"{file_path.relative_to(self.project_root)}:{line_num}",
                            timestamp=self.scan_timestamp,
                            context=context,
                            suggested_fix=pattern.suggested_fix,
                        )
                        errors.append(error)

        except (UnicodeDecodeError, PermissionError, OSError):
            # Skip files that can't be read
            pass

        return errors

    def scan_directory(
        self, directory: Path, extensions: List[str] = None
    ) -> List[DetectedError]:
        """Scan directory for error patterns."""
        if extensions is None:
            extensions = [
                ".py",
                ".log",
                ".txt",
                ".yml",
                ".yaml",
                ".json",
                ".md",
            ]

        errors = []

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                # Skip certain directories
                skip_dirs = {
                    ".git",
                    "__pycache__",
                    ".venv",
                    "node_modules",
                    ".pytest_cache",
                }
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue

                file_errors = self.scan_file_for_errors(file_path)
                errors.extend(file_errors)

        return errors

    def scan_recent_logs(self, hours: int = 24) -> List[DetectedError]:
        """Scan recent log files for errors."""
        errors = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Look for log files
        log_dirs = [
            self.project_root,
            self.project_root / "logs",
            self.project_root / ".github",
        ]

        for log_dir in log_dirs:
            if log_dir.exists():
                for log_file in log_dir.rglob("*.log"):
                    try:
                        if (
                            datetime.fromtimestamp(log_file.stat().st_mtime)
                            >= cutoff_time
                        ):
                            file_errors = self.scan_file_for_errors(log_file)
                            errors.extend(file_errors)
                    except OSError:
                        continue

        return errors

    def check_system_health(self) -> List[DetectedError]:
        """Check system health for potential issues."""
        errors = []

        # Check disk space
        try:
            import shutil

            disk_usage = shutil.disk_usage(self.project_root)
            free_space_gb = disk_usage.free / (1024**3)

            if free_space_gb < 1:  # Less than 1GB free
                error = DetectedError(
                    pattern_name="low_disk_space",
                    severity=ErrorSeverity.HIGH,
                    message=f"Low disk space: {free_space_gb:.2f}GB free",
                    location="system",
                    timestamp=self.scan_timestamp,
                    context=[f"Free space: {free_space_gb:.2f}GB"],
                    suggested_fix="Free up disk space",
                )
                errors.append(error)
        except Exception:
            pass

        # Check Python dependencies
        try:
            pyproject_file = self.project_root / "pyproject.toml"
            if pyproject_file.exists():
                # Try to import key dependencies
                key_deps = ["openai", "supabase", "fastapi", "github"]
                for dep in key_deps:
                    try:
                        __import__(dep)
                    except ImportError:
                        error = DetectedError(
                            pattern_name="missing_dependency",
                            severity=ErrorSeverity.HIGH,
                            message=f"Missing dependency: {dep}",
                            location="dependencies",
                            timestamp=self.scan_timestamp,
                            context=[f"Required dependency '{dep}' not installed"],
                            suggested_fix=f"Install {dep} with 'pip install {dep}' or 'poetry install'",
                        )
                        errors.append(error)
        except Exception:
            pass

        # Check environment variables
        required_env_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
        for env_var in required_env_vars:
            if not os.getenv(env_var):
                error = DetectedError(
                    pattern_name="missing_env_var",
                    severity=ErrorSeverity.HIGH,
                    message=f"Missing environment variable: {env_var}",
                    location="environment",
                    timestamp=self.scan_timestamp,
                    context=[f"Environment variable '{env_var}' not set"],
                    suggested_fix=f"Set {env_var} environment variable",
                )
                errors.append(error)

        return errors

    def run_comprehensive_scan(self) -> Dict[str, Any]:
        """Run comprehensive error detection scan."""
        all_errors = []

        # Scan project files
        project_errors = self.scan_directory(self.project_root)
        all_errors.extend(project_errors)

        # Scan recent logs
        log_errors = self.scan_recent_logs(24)
        all_errors.extend(log_errors)

        # Check system health
        system_errors = self.check_system_health()
        all_errors.extend(system_errors)

        # Categorize errors
        errors_by_severity = defaultdict(list)
        errors_by_pattern = defaultdict(list)

        for error in all_errors:
            errors_by_severity[error.severity.value].append(error)
            errors_by_pattern[error.pattern_name].append(error)

        # Generate summary
        summary = {
            "scan_timestamp": self.scan_timestamp.isoformat(),
            "total_errors": len(all_errors),
            "errors_by_severity": {
                severity.value: len(errors_by_severity[severity.value])
                for severity in ErrorSeverity
            },
            "most_common_patterns": dict(
                Counter(error.pattern_name for error in all_errors).most_common(10)
            ),
            "critical_issues": len(errors_by_severity["critical"]),
            "high_priority_issues": len(errors_by_severity["high"]),
        }

        return {
            "summary": summary,
            "errors": [error.to_dict() for error in all_errors],
            "errors_by_severity": {
                severity: [error.to_dict() for error in errors]
                for severity, errors in errors_by_severity.items()
            },
            "errors_by_pattern": {
                pattern: [error.to_dict() for error in errors]
                for pattern, errors in errors_by_pattern.items()
            },
        }

    def generate_error_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive error report."""
        scan_results = self.run_comprehensive_scan()

        if output_file:
            output_path = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.project_root / f"error_report_{timestamp}.json"

        with open(output_path, "w") as f:
            json.dump(scan_results, f, indent=2, default=str)

        return str(output_path)

    def print_error_summary(self):
        """Print human-readable error summary."""
        scan_results = self.run_comprehensive_scan()
        summary = scan_results["summary"]

        print("🚨 JARVYS Error Detection Report")
        print("=" * 50)
        print(f"Scan Time: {summary['scan_timestamp']}")
        print(f"Total Issues Found: {summary['total_errors']}")
        print()

        # Show severity breakdown
        print("📊 Issues by Severity:")
        severity_colors = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "🔵",
        }

        for severity, count in summary["errors_by_severity"].items():
            if count > 0:
                emoji = severity_colors.get(severity, "⚪")
                print(f"  {emoji} {severity.title()}: {count}")
        print()

        # Show most common patterns
        if summary["most_common_patterns"]:
            print("🔍 Most Common Issues:")
            for pattern, count in list(summary["most_common_patterns"].items())[:5]:
                print(f"  - {pattern.replace('_', ' ').title()}: {count}")
            print()

        # Show critical issues
        critical_errors = scan_results["errors_by_severity"].get("critical", [])
        if critical_errors:
            print("🔴 Critical Issues:")
            for error in critical_errors[:5]:
                print(f"  - {error['message']} ({error['location']})")
                print(f"    Fix: {error['suggested_fix']}")
            print()

        # Show high priority issues
        high_errors = scan_results["errors_by_severity"].get("high", [])
        if high_errors:
            print("🟠 High Priority Issues:")
            for error in high_errors[:5]:
                print(f"  - {error['message']} ({error['location']})")
                print(f"    Fix: {error['suggested_fix']}")
            print()

        # Show recommendations
        print("💡 Recommendations:")
        if summary["critical_issues"] > 0:
            print("  - Address critical issues immediately")
        if summary["high_priority_issues"] > 0:
            print("  - Review and fix high priority issues")
        if summary["total_errors"] == 0:
            print("  - No issues detected - system appears healthy")

        print()


def main():
    """Main entry point for error tracker."""
    tracker = JarvysErrorTracker()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "report":
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            report_path = tracker.generate_error_report(output_file)
            print(f"Error report saved to: {report_path}")

        elif command == "json":
            results = tracker.run_comprehensive_scan()
            print(json.dumps(results, indent=2, default=str))

        elif command == "scan" or command == "check":
            tracker.print_error_summary()

        else:
            print(f"Unknown command: {command}")
            print(
                "Usage: python error_tracker.py [report|json|scan|check] [output_file]"
            )
    else:
        tracker.print_error_summary()


if __name__ == "__main__":
    main()
