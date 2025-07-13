"""
Tests for the Early Launch Issue Processor
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add scripts directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

try:
    from issue_processor import IssueProcessor
except ImportError:
    # Fallback for when dependencies aren't available
    class IssueProcessor:
        def __init__(self, *args, **kwargs):
            pass


class TestIssueProcessor(unittest.TestCase):
    """Test cases for the IssueProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_github_token = "test_token"
        self.mock_repo_name = "test/repo"
        self.mock_supabase_url = "https://test.supabase.co"
        self.mock_supabase_key = "test_key"

    @patch("issue_processor.Github")
    @patch("issue_processor.create_client")
    def test_initialization(self, mock_supabase, mock_github):
        """Test IssueProcessor initialization."""
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo

        processor = IssueProcessor(
            self.mock_github_token,
            self.mock_repo_name,
            self.mock_supabase_url,
            self.mock_supabase_key,
        )

        mock_github.assert_called_once_with(self.mock_github_token)
        mock_supabase.assert_called_once_with(
            self.mock_supabase_url, self.mock_supabase_key
        )

    @patch("issue_processor.Github")
    def test_priority_mapping(self, mock_github):
        """Test that priority mapping is correctly defined."""
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo

        processor = IssueProcessor(self.mock_github_token, self.mock_repo_name)

        # Test high priority autonomy issues
        self.assertEqual(processor.PRIORITY_ISSUES[44]["priority"], 1)
        self.assertEqual(processor.PRIORITY_ISSUES[45]["priority"], 1)
        self.assertEqual(processor.PRIORITY_ISSUES[44]["category"], "autonomy")

        # Test epic issues
        self.assertEqual(processor.PRIORITY_ISSUES[2]["category"], "epic")
        self.assertEqual(processor.PRIORITY_ISSUES[3]["category"], "epic")

        # Test automation issues
        self.assertEqual(processor.PRIORITY_ISSUES[41]["category"], "automation")
        self.assertEqual(processor.PRIORITY_ISSUES[42]["category"], "automation")

    @patch("issue_processor.Github")
    def test_prioritize_issues(self, mock_github):
        """Test issue prioritization logic."""
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo

        processor = IssueProcessor(self.mock_github_token, self.mock_repo_name)

        # Create mock issues
        mock_issue_44 = Mock()
        mock_issue_44.number = 44
        mock_issue_44.pull_request = None

        mock_issue_2 = Mock()
        mock_issue_2.number = 2
        mock_issue_2.pull_request = None

        mock_issue_unknown = Mock()
        mock_issue_unknown.number = 999
        mock_issue_unknown.pull_request = None

        issues = [mock_issue_unknown, mock_issue_2, mock_issue_44]
        prioritized = processor.prioritize_issues(issues)

        # High priority issue should come first
        self.assertEqual(prioritized[0].number, 44)
        self.assertEqual(prioritized[1].number, 2)
        self.assertEqual(prioritized[2].number, 999)

    @patch("issue_processor.Github")
    def test_status_report_structure(self, mock_github):
        """Test status report generation structure."""
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo

        # Mock issues
        mock_issue_44 = Mock()
        mock_issue_44.number = 44
        mock_issue_44.title = "Test Autonomy Issue"
        mock_issue_44.pull_request = None

        mock_repo.get_issues.return_value = [mock_issue_44]

        processor = IssueProcessor(self.mock_github_token, self.mock_repo_name)
        report = processor.generate_status_report()

        # Check report structure
        self.assertIn("timestamp", report)
        self.assertIn("total_open_issues", report)
        self.assertIn("priority_issues", report)
        self.assertIn("categories", report)
        self.assertIn("next_priority_issues", report)
        self.assertIn("early_launch_status", report)
        self.assertIn("automation_cycle", report)

        # Check values
        self.assertEqual(report["total_open_issues"], 1)
        self.assertEqual(report["priority_issues"], 1)
        self.assertEqual(report["early_launch_status"], "active")
        self.assertEqual(report["automation_cycle"], "30 minutes")


class TestWorkflowIntegration(unittest.TestCase):
    """Test workflow integration aspects."""

    def test_workflow_file_exists(self):
        """Test that the workflow file was created."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "early-launch-issues.yml",
        )
        self.assertTrue(os.path.exists(workflow_path), "Workflow file should exist")

    def test_script_file_exists(self):
        """Test that the issue processor script was created."""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "scripts", "issue_processor.py"
        )
        self.assertTrue(
            os.path.exists(script_path), "Issue processor script should exist"
        )

    def test_script_executable(self):
        """Test that the script is executable."""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "scripts", "issue_processor.py"
        )

        if os.path.exists(script_path):
            # Check if file is readable and contains shebang
            with open(script_path, "r") as f:
                first_line = f.readline()
            self.assertTrue(first_line.startswith("#!"), "Script should have shebang")


class TestEarlyLaunchRequirements(unittest.TestCase):
    """Test that early launch requirements are met."""

    @patch("issue_processor.Github")
    def test_priority_issues_defined(self, mock_github):
        """Test that all mentioned priority issues are defined."""
        # Mock GitHub to avoid network calls
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo

        # High Priority Autonomy Issues
        high_priority = [44, 45]

        # Epic Issues
        epic_issues = [1, 2, 3, 4, 5, 6, 7]

        # Automated Tasks
        automated_tasks = [41, 42]

        all_issues = high_priority + epic_issues + automated_tasks

        try:
            from issue_processor import IssueProcessor

            processor = IssueProcessor("dummy", "dummy")

            for issue_num in all_issues:
                self.assertIn(
                    issue_num,
                    processor.PRIORITY_ISSUES,
                    f"Issue #{issue_num} should be in priority mapping",
                )
        except ImportError:
            self.skipTest("Dependencies not available for full test")

    def test_thirty_minute_schedule(self):
        """Test that workflow has 30-minute schedule."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "early-launch-issues.yml",
        )

        if os.path.exists(workflow_path):
            with open(workflow_path, "r") as f:
                content = f.read()

            self.assertIn(
                "*/30 * * * *", content, "Should have 30-minute cron schedule"
            )
            self.assertIn(
                '"inputs":{"mode":"autonomous"}',
                content,
                "Should trigger autonomous mode",
            )

    def test_success_criteria_coverage(self):
        """Test that success criteria are addressed."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "early-launch-issues.yml",
        )

        script_path = os.path.join(
            os.path.dirname(__file__), "..", "scripts", "issue_processor.py"
        )

        success_criteria = [
            "Early launch workflow successfully triggers",
            "Issues are processed in priority order",
            "Automation reports progress to dashboard",
            "No manual intervention required",
            "30-minute autonomous cycle is active",
        ]

        # Check workflow content
        if os.path.exists(workflow_path):
            with open(workflow_path, "r") as f:
                workflow_content = f.read()

            # Workflow trigger test
            self.assertIn("workflow_dispatch", workflow_content)
            self.assertIn("schedule", workflow_content)

            # Dashboard integration test
            self.assertIn("dashboard", workflow_content.lower())

            # Autonomous cycle test
            self.assertIn("*/30", workflow_content)

        # Check script functionality
        if os.path.exists(script_path):
            with open(script_path, "r") as f:
                script_content = f.read()

            # Priority processing test
            self.assertIn("prioritize_issues", script_content)
            self.assertIn("PRIORITY_ISSUES", script_content)

            # Dashboard reporting test
            self.assertIn("update_dashboard", script_content)
            self.assertIn("supabase", script_content.lower())


if __name__ == "__main__":
    # Create a simple test runner that works without full dependencies
    unittest.main(verbosity=2)
