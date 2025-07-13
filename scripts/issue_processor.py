#!/usr/bin/env python3
"""
Early Launch Issue Processor

Automated issue processing script for JARVYS_DEV early launch.
Handles priority-based issue processing, labeling, and progress tracking.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    from github import Github

    from supabase import create_client
except ImportError as e:
    print(f"Required dependencies not installed: {e}")
    print("Run: pip install PyGithub supabase")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class IssueProcessor:
    """Handles automated issue processing for early launch."""

    # Priority mapping for issues
    PRIORITY_ISSUES = {
        # High Priority Autonomy Issues
        44: {
            "priority": 1,
            "category": "autonomy",
            "title": "Intelligence Adaptative",
        },
        45: {
            "priority": 1,
            "category": "autonomy",
            "title": "Apprentissage Continu",
        },
        # Epic Issues (Bootstrap infrastructure first)
        1: {
            "priority": 2,
            "category": "epic",
            "title": "Bootstrap infrastructure",
        },
        2: {
            "priority": 2,
            "category": "epic",
            "title": "Bootstrap infrastructure",
        },
        5: {
            "priority": 2,
            "category": "epic",
            "title": "Bootstrap infrastructure",
        },
        # Core tools
        3: {"priority": 3, "category": "epic", "title": "Core tools"},
        6: {"priority": 3, "category": "epic", "title": "Core tools"},
        # Persona & données
        4: {"priority": 4, "category": "epic", "title": "Persona & données"},
        7: {"priority": 4, "category": "epic", "title": "Persona & données"},
        # Automated Tasks
        41: {
            "priority": 5,
            "category": "automation",
            "title": "Automated task",
        },
        42: {
            "priority": 5,
            "category": "automation",
            "title": "Model detection",
        },
    }

    def __init__(
        self,
        github_token: str,
        repo_name: str,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        """Initialize the issue processor."""
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
        self.supabase = None

        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase: {e}")

    def get_open_issues(self) -> List:
        """Get all open issues from the repository."""
        try:
            issues = list(self.repo.get_issues(state="open"))
            logger.info(f"Found {len(issues)} open issues")
            return issues
        except Exception as e:
            logger.error(f"Failed to fetch issues: {e}")
            return []

    def prioritize_issues(self, issues: List) -> List:
        """Sort issues by priority based on the priority mapping."""

        def get_priority(issue):
            issue_info = self.PRIORITY_ISSUES.get(issue.number, {"priority": 999})
            return issue_info["priority"]

        # Filter out pull requests and sort by priority
        issue_only = [
            issue
            for issue in issues
            if not hasattr(issue, "pull_request") or issue.pull_request is None
        ]
        prioritized = sorted(issue_only, key=get_priority)

        logger.info(f"Prioritized {len(prioritized)} issues")
        return prioritized

    def add_labels_to_issue(self, issue, category: str):
        """Add appropriate labels to an issue based on its category."""
        labels_to_add = []

        if category == "autonomy":
            labels_to_add.extend(
                ["enhancement", "autonomy", "ai-improvement", "high-priority"]
            )
        elif category == "epic":
            labels_to_add.extend(["epic", "infrastructure"])
        elif category == "automation":
            labels_to_add.extend(["automation", "from_jarvys_ai"])

        # Add early-launch label to all processed issues
        labels_to_add.append("early-launch")

        try:
            current_labels = [label.name for label in issue.labels]
            new_labels = [
                label for label in labels_to_add if label not in current_labels
            ]

            if new_labels:
                issue.add_to_labels(*new_labels)
                logger.info(f"Added labels {new_labels} to issue #{issue.number}")
        except Exception as e:
            logger.error(f"Failed to add labels to issue #{issue.number}: {e}")

    def create_progress_comment(self, issue, status: str = "processing"):
        """Add a progress comment to an issue."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        if status == "processing":
            comment_body = f"""🚀 **Early Launch Processing Started**

This issue has been queued for automated processing as part of the JARVYS_DEV early launch initiative.

**Status**: 🔄 Processing
**Priority**: {self.PRIORITY_ISSUES.get(issue.number, {}).get('priority', 'Standard')}
**Category**: {self.PRIORITY_ISSUES.get(issue.number, {}).get('category', 'general')}
**Started**: {timestamp}

The JARVYS_DEV autonomous system will begin working on this issue within the next 30-minute cycle.

---
*This comment was automatically generated by the Early Launch automation system.*"""

        elif status == "analyzed":
            comment_body = f"""📊 **Issue Analysis Complete**

**Analysis completed**: {timestamp}
**Next steps**: Implementation queued for autonomous processing

The issue has been categorized and prepared for the JARVYS_DEV autonomous system.

---
*This comment was automatically generated by the Early Launch automation system.*"""

        try:
            issue.create_comment(comment_body)
            logger.info(f"Added progress comment to issue #{issue.number}")
        except Exception as e:
            logger.error(f"Failed to add comment to issue #{issue.number}: {e}")

    def log_to_supabase(self, issue_data: Dict):
        """Log issue processing data to Supabase."""
        if not self.supabase:
            logger.warning("Supabase not available, skipping logging")
            return

        try:
            # Try to insert into a jarvys_issue_processing table
            data = {
                "issue_number": issue_data["number"],
                "title": issue_data["title"],
                "priority": issue_data["priority"],
                "category": issue_data["category"],
                "status": issue_data["status"],
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "repository": issue_data.get("repository", "yannabadie/appia-dev"),
            }

            result = (
                self.supabase.table("jarvys_issue_processing").insert(data).execute()
            )
            logger.info(f"Logged issue #{issue_data['number']} to Supabase")
        except Exception as e:
            logger.warning(f"Failed to log to Supabase: {e}")

    def process_priority_issues(self) -> Dict:
        """Process issues based on priority."""
        logger.info("🔍 Starting priority issue processing...")

        issues = self.get_open_issues()
        if not issues:
            return {"processed": 0, "errors": 0}

        prioritized_issues = self.prioritize_issues(issues)
        processed_count = 0
        error_count = 0

        # Process top 5 priority issues in this run
        for issue in prioritized_issues[:5]:
            try:
                issue_info = self.PRIORITY_ISSUES.get(
                    issue.number,
                    {
                        "priority": 999,
                        "category": "general",
                        "title": issue.title,
                    },
                )

                logger.info(f"Processing issue #{issue.number}: {issue.title}")

                # Add labels
                self.add_labels_to_issue(issue, issue_info["category"])

                # Add progress comment
                self.create_progress_comment(issue, "processing")

                # Log to Supabase
                self.log_to_supabase(
                    {
                        "number": issue.number,
                        "title": issue.title,
                        "priority": issue_info["priority"],
                        "category": issue_info["category"],
                        "status": "queued_for_processing",
                    }
                )

                processed_count += 1

            except Exception as e:
                logger.error(f"Error processing issue #{issue.number}: {e}")
                error_count += 1

        logger.info(f"✅ Processed {processed_count} issues, {error_count} errors")
        return {"processed": processed_count, "errors": error_count}

    def update_dashboard(self) -> Dict:
        """Update Supabase dashboard with current status."""
        logger.info("📊 Updating dashboard...")

        if not self.supabase:
            logger.warning("Supabase not available for dashboard update")
            return {"status": "no_supabase"}

        try:
            issues = self.get_open_issues()
            priority_issues = [i for i in issues if i.number in self.PRIORITY_ISSUES]

            dashboard_data = {
                "total_open_issues": len(issues),
                "priority_issues": len(priority_issues),
                "last_update": datetime.now(timezone.utc).isoformat(),
                "early_launch_active": True,
                "next_cycle": "30 minutes",
            }

            # Try to update a dashboard status table
            result = (
                self.supabase.table("jarvys_dashboard_status")
                .upsert(dashboard_data)
                .execute()
            )
            logger.info("Dashboard updated successfully")
            return {"status": "success", "data": dashboard_data}

        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")
            return {"status": "error", "error": str(e)}

    def generate_status_report(self) -> Dict:
        """Generate a comprehensive status report."""
        logger.info("📈 Generating status report...")

        issues = self.get_open_issues()
        prioritized_issues = self.prioritize_issues(issues)

        # Count issues by category
        categories = {}
        for issue in issues:
            if issue.number in self.PRIORITY_ISSUES:
                category = self.PRIORITY_ISSUES[issue.number]["category"]
                categories[category] = categories.get(category, 0) + 1

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_open_issues": len(issues),
            "priority_issues": len(
                [i for i in issues if i.number in self.PRIORITY_ISSUES]
            ),
            "categories": categories,
            "next_priority_issues": [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "priority": self.PRIORITY_ISSUES.get(issue.number, {}).get(
                        "priority", 999
                    ),
                }
                for issue in prioritized_issues[:3]
            ],
            "early_launch_status": "active",
            "automation_cycle": "30 minutes",
        }

        # Print report to console
        print("\n" + "=" * 60)
        print("🚀 EARLY LAUNCH STATUS REPORT")
        print("=" * 60)
        print(f"📅 Generated: {report['timestamp']}")
        print(f"📋 Total Open Issues: {report['total_open_issues']}")
        print(f"⭐ Priority Issues: {report['priority_issues']}")
        print(f"🔄 Next Cycle: {report['automation_cycle']}")
        print("\n📊 Issues by Category:")
        for category, count in report["categories"].items():
            print(f"   {category}: {count}")
        print("\n🎯 Next Priority Issues:")
        for item in report["next_priority_issues"]:
            print(
                f"   #{item['number']}: {item['title']} (Priority: {item['priority']})"
            )
        print("=" * 60)

        return report


def main():
    """Main entry point for the issue processor."""
    parser = argparse.ArgumentParser(description="Early Launch Issue Processor")
    parser.add_argument(
        "--mode",
        choices=["priority", "dashboard_update", "status_report"],
        default="priority",
        help="Processing mode",
    )

    args = parser.parse_args()

    # Get environment variables
    github_token = os.getenv("GH_TOKEN")
    repo_name = os.getenv("GH_REPO", "yannabadie/appia-dev")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not github_token:
        logger.error("GH_TOKEN environment variable required")
        sys.exit(1)

    # Initialize processor
    processor = IssueProcessor(github_token, repo_name, supabase_url, supabase_key)

    # Execute based on mode
    if args.mode == "priority":
        result = processor.process_priority_issues()
        print(f"🎯 Priority processing completed: {result}")

    elif args.mode == "dashboard_update":
        result = processor.update_dashboard()
        print(f"📊 Dashboard update completed: {result}")

    elif args.mode == "status_report":
        result = processor.generate_status_report()

        # Save report to file
        report_file = (
            f"early_launch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"📄 Report saved to: {report_file}")

    logger.info("Early launch processing completed")


if __name__ == "__main__":
    main()
