"""
GitHub helpers.

Secrets nécessaires : GH_TOKEN, GH_REPO
"""

from __future__ import annotations

import os

from github import Github


def github_create_issue(
    title: str,
    body: str = "",
    *,
    labels: list[str] | None = None,
    repo_fullname: str | None = None,
) -> str:
    labels = labels or []
    gh_token = os.getenv("GH_TOKEN")
    repo_fullname = repo_fullname or os.getenv("GH_REPO")
    if not gh_token or not repo_fullname:
        raise RuntimeError("GH_TOKEN ou GH_REPO manquant.")

    gh = Github(gh_token)
    repo = gh.get_repo(repo_fullname)

    for iss in repo.get_issues(state="open"):
        if iss.title == title:
            return iss.html_url

    issue = repo.create_issue(title=title, body=body, labels=labels)
    return issue.html_url
