#!/usr/bin/env python3
# --- bootstrap_jarvys_dev.py (idempotent – Projects v2) --------------------
"""
Bootstrap JARVYS_DEV : crée/maj Project v2, issues, workflow CI, devcontainer,
tool stub. Relançable sans erreur.

Dépend de : GH_TOKEN, GH_REPO, SUPABASE_URL, SUPABASE_KEY,
            GCP_SA_JSON, OPENAI_API_KEY, GEMINI_API_KEY
"""

import os
import subprocess
import sys
import textwrap
from typing import List


# ---------- petites fonctions utilitaires ----------
def _pip(pkg: str):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pkg])


try:
    from github import Github, GithubException
except ImportError:
    _pip("PyGithub>=2.6")
    from github import Github, GithubException
try:
    pass
except ImportError:
    _pip("requests")

# ---------- variables d'environnement ----------
env = {
    k: os.getenv(k)
    for k in (
        "GH_TOKEN",
        "GH_REPO",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "GCP_SA_JSON",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "SECRET_ACCESS_TOKEN",
    )
}
miss = [k for k, v in env.items() if not v]
if miss:
    sys.exit("❌  Variables manquantes : " + ", ".join(miss))


def _check_branch(expected: str = "main") -> None:
    cur = (
        subprocess.check_output(["git", "rev-parse", "--abbrev-re", "HEAD"])
        .decode()
        .strip()
    )
    if cur != expected:
        sys.exit(f"❌  Doit être sur la branche {expected}, pas {cur}")


def _run_checks() -> None:
    subprocess.check_call(
        [
            "poetry",
            "run",
            "pre-commit",
            "run",
            "--files",
            ".",
        ]
    )
    subprocess.check_call(["poetry", "run", "pytest", "-q"])


_check_branch()
_run_checks()

gh = Github(env["GH_TOKEN"])
repo = gh.get_repo(env["GH_REPO"])
owner = repo.owner.login

# ---------- aide GraphQL ----------
GQL = "https://api.github.com/graphql"
HEAD = {"Authorization": f"bearer {env['GH_TOKEN']}"}


def gql(query: str, **vars):
    import textwrap

    import requests

    r = requests.post(
        GQL,
        headers=HEAD,
        json={"query": textwrap.dedent(query), "variables": vars},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


# ---------- Project v2 ----------
PROJECT_TITLE = "JARVYS_DEV Roadmap"


def get_or_create_project() -> str:
    q = """
      query($login:String!){
        user(login:$login){
          id
          projectsV2(first:100){
            nodes{ id title url }
          }
        }
      }
    """
    d = gql(q, login=owner)["user"]
    for n in d["projectsV2"]["nodes"]:
        if n["title"] == PROJECT_TITLE:
            print(f"ℹ️  Project déjà présent : {n['url']}")
            return n["id"]
    mut = """
      mutation($owner:ID!,$title:String!){
        createProjectV2(input:{ownerId:$owner,title:$title}){
          projectV2{ id url }
        }
      }
    """
    proj = gql(mut, owner=d["id"], title=PROJECT_TITLE)["createProjectV2"]["projectV2"]
    print(f"✅  Project créé : {proj['url']}")
    return proj["id"]


def add_issue_to_project(pid: str, node_id: str):
    mut = """
      mutation($p:ID!,$c:ID!){
        addProjectV2ItemById(input:{projectId:$p,contentId:$c}){ item{ id } }
      }"""
    gql(mut, p=pid, c=node_id)


def issue_node_id(num: int) -> str:
    q = """
      query($o:String!,$r:String!,$n:Int!){
        repository(owner:$o,name:$r){ issue(number:$n){ id } }
      }"""
    return gql(q, o=owner, r=repo.name, n=num)["repository"]["issue"]["id"]


# ---------- helper upsert (create ou update) ----------
def upsert(path: str, message: str, content: str, branch="main"):
    try:
        cur = repo.get_contents(path, ref=branch)
        repo.update_file(path, message, content, cur.sha, branch=branch)
    except GithubException as e:
        if e.status == 404:
            repo.create_file(path, message, content, branch=branch)
        else:
            raise


# ---------- 1) project & issues ----------
pid = get_or_create_project()

ISSUES: List[tuple[str, str]] = [
    (
        "Epic : Bootstrap infrastructure",
        "- [ ] Stocker OPENAI_API_KEY dans GitHub Secrets\n"
        "- [ ] Générer la clé ServiceAccount GCP\n"
        "- [ ] Créer projet Supabase `jarvys_dev_mem`\n"
        "- [ ] Ajouter workflow `ci.yml`",
    ),
    (
        "Epic : Core tools",
        "- [ ] Implémenter `github_create_issue`\n"
        "- [ ] Implémenter `memory_search`\n"
        "- [ ] Tests unitaires tools",
    ),
    (
        "Epic : Persona & données Yann",
        "- [ ] Export PDF LinkedIn\n" "- [ ] Script `load_linkedin.py` ➜ Supabase",
    ),
]

open_titles = {_i.title for _i in repo.get_issues(state="open")}
for title, body in ISSUES:
    if title in open_titles:
        print(f"⚠️  Issue « {title} » déjà ouverte — saut")
        continue
    issue = repo.create_issue(title, body)
    node = getattr(issue, "node_id", None) or issue_node_id(issue.number)
    add_issue_to_project(pid, node)
    print(f"✅  Issue créée : #{issue.number} – {title}")

# ---------- 2) workflow CI ----------
ci = textwrap.dedent(
    """\
    name: CI
    on: [push, pull_request]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: '3.12'
          - run: pip install poetry
          - run: poetry install
          - run: poetry run pytest
"""
)
upsert(".github/workflows/ci.yml", "Add/Update CI workflow", ci)

# ---------- 3) devcontainer ----------
devc = textwrap.dedent(
    """\
{
  "name": "jarvys_dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "pip install poetry",
  "forwardPorts": [54321],
  "containerEnv": {
    "GH_TOKEN": "${{ secrets.GH_TOKEN }}",
    "GH_REPO": "${{ secrets.GH_REPO }}",
    "SECRET_ACCESS_TOKEN": "${{ secrets.SECRET_ACCESS_TOKEN }}"
  }
}"""
)
upsert(".devcontainer/devcontainer.json", "Add/Update devcontainer config = {}", devc)

# ---------- 4) tool stub ----------
stub = textwrap.dedent(
    """\
\"\"\"GitHub tools for JARVYS_DEV.\"\"\"

def github_create_issue(title: str, body: str = "") -> str:
    \"\"\"Create a GitHub issue.
    
    Args:
        title: Issue title
        body: Issue body (optional)
        
    Returns:
        Issue URL
    \"\"\"
    # TODO: Implement GitHub issue creation
    pass

def github_search_issues(query: str) -> list:
    \"\"\"Search GitHub issues.
    
    Args:
        query: Search query
        
    Returns:
        List of matching issues
    \"\"\"
    # TODO: Implement GitHub issue search
    pass
"""
)
upsert("src/jarvys_dev/tools/github_tools.py", "Add/Update tool stub", stub)

print("🎉  Bootstrap terminé — relançable sans duplication ni erreur.")
# ------------------------------------------------------------------- EOF
