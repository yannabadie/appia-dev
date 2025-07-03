"""
GitHub helpers.

Secrets nécessaires : GH_TOKEN, GH_REPO
"""

from __future__ import annotations

import json
import os

from github import Github
from openai import OpenAI


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


def copilot_generate_patch(
    files: dict[str, str], prompt: str
) -> tuple[dict[str, str], str]:
    """Generate multi-file changes and a commit message via OpenAI."""
    gh_token = os.getenv("GH_TOKEN")
    if not gh_token:
        raise RuntimeError("GH_TOKEN manquant")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY manquant")

    client = OpenAI(api_key=api_key)
    payload = json.dumps({"prompt": prompt, "files": files})
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are GitHub Copilot"},
            {"role": "user", "content": payload},
        ],
    )
    data = json.loads(resp.choices[0].message.content)
    return data.get("files", {}), data.get("message", "")
