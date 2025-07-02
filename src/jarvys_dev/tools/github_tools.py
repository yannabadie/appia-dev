# src/jarvys_dev/tools/github_tools.py
"""
Fonctions d’intégration GitHub.

Secrets requis :
- GH_TOKEN : PAT avec scopes `repo`, `project`.
- GH_REPO  : nom complet du dépôt (ex. "yannabadie/appia-dev").
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
    """Crée une issue (ou renvoie celle déjà ouverte portant le même titre).

    Args:
        title: Titre de l’issue.
        body:  Corps Markdown.
        labels: étiquettes à appliquer.
        repo_fullname: "<owner>/<repo>" (sinon lit GH_REPO dans les secrets).

    Returns:
        URL HTML de l’issue.
    """
    labels = labels or []
    gh_token = os.getenv("GH_TOKEN")
    repo_fullname = repo_fullname or os.getenv("GH_REPO")

    if not gh_token or not repo_fullname:
        raise RuntimeError("Secrets GH_TOKEN ou GH_REPO manquants.")

    gh = Github(gh_token)
    repo = gh.get_repo(repo_fullname)

    # Dé‑duplication sur le titre
    for iss in repo.get_issues(state="open"):
        if iss.title == title:
            return iss.html_url

    new_issue = repo.create_issue(title=title, body=body, labels=labels)
    return new_issue.html_url
