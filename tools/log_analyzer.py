import os
"""Centralized log analysis for JARVYS ecosystem."""

import gzip
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class JarvysLogAnalyzer:
    """Centralized log analyzer for JARVYS ecosystem."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.analysis_timestamp = datetime.now()

    def find_log_files(self) -> List[Path]:
        """Find all log files in the project."""
        log_files = []

        # Common log file patterns
        log_patterns = ["*.log", "*.out", "*.err", "*.txt"]

        # Search in common log locations
        search_dirs = [
            self.project_root,
            self.project_root / "logs",
            self.project_root / ".github",
            self.project_root / "tmp",
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in log_patterns:
                    log_files.extend(search_dir.rglob(pattern))

        # Filter to actual log files (by content/name)
        actual_log_files = []
        for log_file in log_files:
            if self._is_log_file(log_file):
                actual_log_files.append(log_file)

        return actual_log_files

    def _is_log_file(self, file_path: Path) -> bool:
        """Determine if a file is actually a log file."""
        # Skip certain files
        skip_patterns = [
            r"\.git/",
            r"node_modules/",
            r"__pycache__/",
            r"\.venv/",
            r"\.pytest_cache/",
            r"requirements.*\.txt$",
            r"README.*\.txt$",
            r"LICENSE.*\.txt$",
        ]

        file_str = str(file_path)
        for pattern in skip_patterns:
            if re.search(pattern, file_str):
                return False

        # Check if file looks like a log
        log_indicators = [
            "log",
            "debug",
            "error",
            "warn",
            "info",
            "output",
            "trace",
            "audit",
        ]

        file_name_lower = file_path.name.lower()
        if any(indicator in file_name_lower for indicator in log_indicators):
            return True

        # Check file content for log patterns
        try:
            if file_path.stat().st_size > 50 * 1024 * 1024:  # Skip files > 50MB
                return False

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_lines = f.read(1024)

            # Look for timestamp patterns (common in logs)
            timestamp_patterns = [
                r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
                r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
                r"\[\d{2}:\d{2}:\d{2}\]",  # [HH:MM:SS]
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO format
            ]

            for pattern in timestamp_patterns:
                if re.search(pattern, first_lines):
                    return True

        except (UnicodeDecodeError, PermissionError, OSError):
            return False

        return False

    def parse_log_file(self, log_file: Path) -> Dict[str, Any]:
        """Parse a single log file."""
        analysis = {
            "file_info": {
                "path": str(log_file.relative_to(self.project_root)),
                "size_bytes": log_file.stat().st_size,
                "modified": datetime.fromtimestamp(
                    log_file.stat().st_mtime
                ).isoformat(),
                "age_hours": (
                    datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)
                ).total_seconds()
                / 3600,
            },
            "content_analysis": {
                "total_lines": 0,
                "error_count": 0,
                "warning_count": 0,
                "info_count": 0,
                "debug_count": 0,
            },
            "patterns": {
                "errors": [],
                "warnings": [],
                "exceptions": [],
                "api_calls": [],
                "timestamps": [],
            },
            "keywords": Counter(),
            "recent_entries": [],
        }

        try:
            # Handle compressed logs
            if log_file.suffix == ".gz":
                file_opener = gzip.open
                mode = "rt"
            else:
                file_opener = open
                mode = "r"

            with file_opener(log_file, mode, encoding="utf-8", errors="ignore") as f:
                lines = []
                for line_num, line in enumerate(f, 1):
                    if line_num > 10000:  # Limit to avoid memory issues
                        break
                    lines.append(line.strip())

                analysis["content_analysis"]["total_lines"] = len(lines)

                # Analyze each line
                for line in lines:
                    self._analyze_log_line(line, analysis)

                # Get recent entries (last 50 lines)
                analysis["recent_entries"] = lines[-50:] if lines else []

        except Exception as e:
            analysis["error"] = f"Failed to parse: {str(e)}"

        return analysis

    def _analyze_log_line(self, line: str, analysis: Dict[str, Any]):
        """Analyze a single log line."""
        line_lower = line.lower()

        # Count log levels
        if any(
            pattern in line_lower for pattern in ["error", "err", "failed", "exception"]
        ):
            analysis["content_analysis"]["error_count"] += 1
            if len(analysis["patterns"]["errors"]) < 10:
                analysis["patterns"]["errors"].append(line[:200])

        if any(pattern in line_lower for pattern in ["warning", "warn", "deprecated"]):
            analysis["content_analysis"]["warning_count"] += 1
            if len(analysis["patterns"]["warnings"]) < 10:
                analysis["patterns"]["warnings"].append(line[:200])

        if any(pattern in line_lower for pattern in ["info", "information"]):
            analysis["content_analysis"]["info_count"] += 1

        if any(pattern in line_lower for pattern in ["debug", "trace", "verbose"]):
            analysis["content_analysis"]["debug_count"] += 1

        # Look for exceptions
        if any(pattern in line for pattern in ["Exception", "Error:", "Traceback"]):
            if len(analysis["patterns"]["exceptions"]) < 10:
                analysis["patterns"]["exceptions"].append(line[:200])

        # Look for API calls
        if any(
            pattern in line_lower for pattern in ["http", "api", "request", "response"]
        ):
            if len(analysis["patterns"]["api_calls"]) < 10:
                analysis["patterns"]["api_calls"].append(line[:200])

        # Extract timestamps
        timestamp_patterns = [
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
            r"\[\d{2}:\d{2}:\d{2}\]",
        ]

        for pattern in timestamp_patterns:
            matches = re.findall(pattern, line)
            if matches and len(analysis["patterns"]["timestamps"]) < 20:
                analysis["patterns"]["timestamps"].extend(matches)

        # Extract keywords (excluding common words)
        common_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "o",
            "with",
            "by",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "this",
            "that",
            "these",
            "those",
            "it",
            "they",
            "them",
            "their",
            "there",
        }

        words = re.findall(r"\b[a-zA-Z]{3,}\b", line_lower)
        for word in words:
            if word not in common_words:
                analysis["keywords"][word] += 1

    def analyze_all_logs(self) -> Dict[str, Any]:
        """Analyze all log files in the project."""
        log_files = self.find_log_files()

        overall_analysis = {
            "timestamp": self.analysis_timestamp.isoformat(),
            "summary": {
                "total_log_files": len(log_files),
                "total_size_mb": 0,
                "oldest_log": None,
                "newest_log": None,
                "total_errors": 0,
                "total_warnings": 0,
                "total_lines": 0,
            },
            "files": {},
            "aggregated_patterns": {
                "common_errors": Counter(),
                "common_warnings": Counter(),
                "frequent_keywords": Counter(),
                "api_activity": [],
            },
            "trends": {
                "error_frequency": defaultdict(int),
                "activity_by_hour": defaultdict(int),
            },
        }

        if not log_files:
            overall_analysis["message"] = "No log files found"
            return overall_analysis

        # Analyze each log file
        for log_file in log_files:
            file_analysis = self.parse_log_file(log_file)
            overall_analysis["files"][
                str(log_file.relative_to(self.project_root))
            ] = file_analysis

            # Update summary
            file_info = file_analysis["file_info"]
            content_analysis = file_analysis["content_analysis"]

            overall_analysis["summary"]["total_size_mb"] += file_info["size_bytes"] / (
                1024 * 1024
            )
            overall_analysis["summary"]["total_errors"] += content_analysis[
                "error_count"
            ]
            overall_analysis["summary"]["total_warnings"] += content_analysis[
                "warning_count"
            ]
            overall_analysis["summary"]["total_lines"] += content_analysis[
                "total_lines"
            ]

            # Track oldest/newest
            file_age = file_info["age_hours"]
            if (
                overall_analysis["summary"]["oldest_log"] is None
                or file_age > overall_analysis["summary"]["oldest_log"]
            ):
                overall_analysis["summary"]["oldest_log"] = file_age
            if (
                overall_analysis["summary"]["newest_log"] is None
                or file_age < overall_analysis["summary"]["newest_log"]
            ):
                overall_analysis["summary"]["newest_log"] = file_age

            # Aggregate patterns
            for error in file_analysis["patterns"]["errors"]:
                # Extract error type
                error_type = self._extract_error_type(error)
                overall_analysis["aggregated_patterns"]["common_errors"][
                    error_type
                ] += 1

            for warning in file_analysis["patterns"]["warnings"]:
                warning_type = self._extract_error_type(warning)
                overall_analysis["aggregated_patterns"]["common_warnings"][
                    warning_type
                ] += 1

            # Aggregate keywords
            overall_analysis["aggregated_patterns"]["frequent_keywords"].update(
                file_analysis["keywords"]
            )

        # Round total size
        overall_analysis["summary"]["total_size_mb"] = round(
            overall_analysis["summary"]["total_size_mb"], 2
        )

        # Convert Counters to regular dicts for JSON serialization
        overall_analysis["aggregated_patterns"]["common_errors"] = dict(
            overall_analysis["aggregated_patterns"]["common_errors"].most_common(10)
        )
        overall_analysis["aggregated_patterns"]["common_warnings"] = dict(
            overall_analysis["aggregated_patterns"]["common_warnings"].most_common(10)
        )
        overall_analysis["aggregated_patterns"]["frequent_keywords"] = dict(
            overall_analysis["aggregated_patterns"]["frequent_keywords"].most_common(20)
        )

        return overall_analysis

    def _extract_error_type(self, error_line: str) -> str:
        """Extract error type from error line."""
        # Look for common error patterns
        patterns = [
            r"(\w+Error):",
            r"(\w+Exception):",
            r"ERROR:\s*(\w+)",
            r"FAILED\s*(\w+)",
            r"(\w+)\s*failed",
        ]

        for pattern in patterns:
            match = re.search(pattern, error_line, re.IGNORECASE)
            if match:
                return match.group(1).lower()

        # Fallback to first word
        words = error_line.split()
        if words:
            return words[0].lower()[:20]

        return "unknown"

    def generate_log_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive log analysis report."""
        analysis = self.analyze_all_logs()

        if output_file:
            output_path = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.project_root / f"log_analysis_{timestamp}.json"

        with open(output_path, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        return str(output_path)

    def print_log_summary(self):
        """Print human-readable log analysis summary."""
        analysis = self.analyze_all_logs()

        print("📋 JARVYS Log Analysis Summary")
        print("=" * 50)
        print(f"Analysis Time: {analysis['timestamp']}")
        print()

        summary = analysis["summary"]
        print("📊 Overview:")
        print(f"  Log Files Found: {summary['total_log_files']}")
        print(f"  Total Size: {summary['total_size_mb']} MB")
        print(f"  Total Lines: {summary['total_lines']:,}")
        print(f"  Total Errors: {summary['total_errors']:,}")
        print(f"  Total Warnings: {summary['total_warnings']:,}")

        if summary["oldest_log"] is not None:
            print(f"  Oldest Log: {summary['oldest_log']:.1f} hours ago")
        if summary["newest_log"] is not None:
            print(f"  Newest Log: {summary['newest_log']:.1f} hours ago")
        print()

        # Show most common errors
        if analysis["aggregated_patterns"]["common_errors"]:
            print("🚨 Most Common Errors:")
            for error_type, count in list(
                analysis["aggregated_patterns"]["common_errors"].items()
            )[:5]:
                print(f"  - {error_type}: {count} occurrences")
            print()

        # Show most common warnings
        if analysis["aggregated_patterns"]["common_warnings"]:
            print("⚠️  Most Common Warnings:")
            for warning_type, count in list(
                analysis["aggregated_patterns"]["common_warnings"].items()
            )[:5]:
                print(f"  - {warning_type}: {count} occurrences")
            print()

        # Show frequent keywords
        if analysis["aggregated_patterns"]["frequent_keywords"]:
            print("🔍 Frequent Keywords:")
            keywords = list(
                analysis["aggregated_patterns"]["frequent_keywords"].items()
            )[:10]
            keyword_str = ", ".join([f"{k}({v})" for k, v in keywords])
            print(f"  {keyword_str}")
            print()

        # Show file breakdown
        if analysis["files"]:
            print("📁 Log Files:")
            for file_path, file_analysis in list(analysis["files"].items())[:10]:
                errors = file_analysis["content_analysis"]["error_count"]
                warnings = file_analysis["content_analysis"]["warning_count"]
                size_kb = file_analysis["file_info"]["size_bytes"] / 1024

                print(f"  - {file_path} ({size_kb:.1f} KB)")
                if errors > 0 or warnings > 0:
                    print(f"    Errors: {errors}, Warnings: {warnings}")

        print()


def main():
    """Main entry point for log analyzer."""
    analyzer = JarvysLogAnalyzer()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "report":
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            report_path = analyzer.generate_log_report(output_file)
            print(f"Log analysis report saved to: {report_path}")

        elif command == "json":
            analysis = analyzer.analyze_all_logs()
            print(json.dumps(analysis, indent=2, default=str))

        elif command == "summary" or command == "analyze":
            analyzer.print_log_summary()

        else:
            print(f"Unknown command: {command}")
            print(
                "Usage: python log_analyzer.py [report|json|summary|analyze] [output_file]"
            )
    else:
        analyzer.print_log_summary()


if __name__ == "__main__":
    import sys

    main()
