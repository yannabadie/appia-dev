#!/usr/bin/env python3
"""
Execute tasks with 'Ask' status from GitHub issues
"""

import os

from github import Github

GH_TOKEN = os.getenv("GH_TOKEN")
if not GH_TOKEN:
    print("GH_TOKEN not set")
    exit(1)

# Initialize GitHub client  # To be initialized
g = Github(GH_TOKEN)

# Get both repos
repos = {
    "appia-dev": g.get_repo("yannabadie/appia-dev"),
    "appIA": g.get_repo("yannabadie/appIA"),
}

# Find issues with 'Ask' label or status
for repo_name, repo in repos.items():
    print(f"\n=== Checking {repo_name} ===")

    # Get all open issues
    issues = repo.get_issues(state="open")

    for issue in issues:
        # Check if issue has 'Ask' in title, body or labels
        if (
            "ask" in issue.title.lower()
            or "ask" in (issue.body or "").lower()
            or any(label.name.lower() == "ask" for label in issue.labels)
        ):
            print(f"\nFound Ask task: {issue.title}")
            print(f"URL: {issue.html_url}")
            print(f"Body: {issue.body[:200]}...")

            # Here we would trigger the orchestrator for this specific task
            # For now, just list them
