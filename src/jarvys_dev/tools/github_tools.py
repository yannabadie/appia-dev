"""
GitHub helpers.

Secrets nécessaires : GH_TOKEN, GH_REPO
"""

from __future__ import annotations

import json
import os
import subprocess

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

    _client = OpenAI(api_key=api_key)
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


def copilot_commit_patch(
    files: dict[str, str], prompt: str, branch: str = "dev"
) -> str:
    """Generate changes with Copilot, write files and commit them."""
    new_files, message = copilot_generate_patch(files, prompt)
    cur = (
        subprocess.check_output(["git", "rev-parse", "--abbrev-re", "HEAD"])
        .decode()
        .strip()
    )
    if cur != branch:
        raise RuntimeError(f"Current branch {cur} is not {branch}")
    for path, content in new_files.items():
        with open(path, "w") as fh:
            fh.write(content)
    subprocess.check_call(["git", "add", *new_files.keys()])
    subprocess.check_call(["git", "commit", "-m", message])
    return message


def create_pull_request(
    title: str,
    body: str = "",
    *,
    head: str | None = None,
    base: str = "main",
    repo_fullname: str | None = None,
) -> str:
    """Create a pull request targeting the ``main`` branch."""
    if base not in ["main", "dev"]:
        raise ValueError("PRs must target the 'main' or 'dev' branch")

    gh_token = os.getenv("GH_TOKEN")
    repo_fullname = repo_fullname or os.getenv("GH_REPO")
    if not gh_token or not repo_fullname:
        raise RuntimeError("GH_TOKEN ou GH_REPO manquant.")

    gh = Github(gh_token)
    repo = gh.get_repo(repo_fullname)
    head = head or repo.default_branch
    pr = repo.create_pull(title=title, body=body, head=head, base=base)
    return pr.html_url
