from __future__ import annotations
import os
from typing import List, Optional

from github import Github, GithubException


def _get_repo() -> "Repository":
    """Retourne l’objet Repo en se basant sur GH_TOKEN et GH_REPO."""
    gh_token = os.getenv("GH_TOKEN")
    gh_repo  = os.getenv("GH_REPO")
    if not gh_token or not gh_repo:
        raise RuntimeError("GH_TOKEN or GH_REPO env var missing")
    try:
        gh = Github(gh_token)
        return gh.get_repo(gh_repo)
    except GithubException as exc:
        raise RuntimeError("GitHub authentication failed") from exc


def github_create_issue(
    title: str,
    body: str = "",
    labels: Optional[List[str]] = None,
) -> int:
    """
    Crée une issue.  Si `title` existe déjà (issue ouverte), ne recrée pas.
    Retourne le numéro d’issue.
    """
    repo = _get_repo()

    # 1) duplication ?
    for issue in repo.get_issues(state="open"):
        if issue.title == title:
            return issue.number

    # 2) Création
    issue = repo.create_issue(title=title, body=body)

    # 3) Labels éventuels
    if labels:
        existing = {lbl.name for lbl in repo.get_labels()}
        for lbl in labels:
            if lbl not in existing:
                repo.create_label(name=lbl, color="BFD4F2")
        issue.edit(labels=labels)

    return issue.number
