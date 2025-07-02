# --- bootstrap_jarvys_dev.py (idempotent, Projects v2) -----------------------
#!/usr/bin/env python3
"""
Bootstrap JARVYS_DEV : crée/maj Project v2, issues, workflow CI, devcontainer,
stubs de tools. Relançable sans erreur.

Env : GH_TOKEN, GH_REPO, SUPABASE_URL, SUPABASE_KEY,
      GCP_SA_JSON, OPENAI_API_KEY, GEMINI_API_KEY
"""
import os, sys, textwrap, pathlib, subprocess
from typing import Optional

# -------------------------------------------------------------------- utils
def _pip(pkg: str):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pkg])

try:
    from github import Github, GithubException
except ImportError:
    _pip("PyGithub>=2.4.0")
    from github import Github, GithubException
try:
    import requests
except ImportError:
    _pip("requests")
    import requests

# ------------------------------------------------------------------ env vars
env = {k: os.getenv(k) for k in (
    "GH_TOKEN","GH_REPO","SUPABASE_URL","SUPABASE_KEY",
    "GCP_SA_JSON","OPENAI_API_KEY","GEMINI_API_KEY"
)}
missing = [k for k,v in env.items() if not v]
if missing:
    sys.exit("❌  Variables manquantes : " + ", ".join(missing))

gh    = Github(env["GH_TOKEN"])
repo  = gh.get_repo(env["GH_REPO"])
owner = repo.owner.login

# ----------------------------------------------------------- GraphQL helper
GQL = "https://api.github.com/graphql"
HDR = {"Authorization": f"bearer {env['GH_TOKEN']}", "Content-Type":"application/json"}
def gql(q: str, **vars):
    import json, requests
    r = requests.post(GQL, headers=HDR,
                      json={"query": textwrap.dedent(q), "variables": vars}, timeout=30)
    r.raise_for_status()
    d = r.json()
    if d.get("errors"):
        raise RuntimeError(d["errors"])
    return d["data"]

# ----------------------------------------------------------- Project v2 CRUD
PROJECT_TITLE = "JARVYS_DEV Roadmap"

def project_v2_id() -> str:
    q = """
      query($login:String!){
        user(login:$login){
          id projectsV2(first:100){ nodes{ id title url } }
        }
      }"""
    d = gql(q, login=owner)["user"]
    for n in d["projectsV2"]["nodes"]:
        if n["title"] == PROJECT_TITLE:
            print(f"ℹ️  Project déjà présent : {n['url']}")
            return n["id"]
    # create
    mut = """
      mutation($owner:ID!,$title:String!){
        createProjectV2(input:{ownerId:$owner,title:$title}){ projectV2{ id url } }
      }"""
    proj = gql(mut, owner=d["id"], title=PROJECT_TITLE)["createProjectV2"]["projectV2"]
    print(f"✅  Project créé : {proj['url']}")
    return proj["id"]

def project_add_issue(pid: str, node_id: str):
    mut = """
      mutation($p:ID!,$c:ID!){
        addProjectV2ItemById(input:{projectId:$p,contentId:$c}){ item{ id } }
      }"""
    gql(mut, p=pid, c=node_id)

def issue_node_id(num: int) -> str:
    q = """
      query($owner:String!,$repo:String!,$n:Int!){
        repository(owner:$owner,name:$repo){ issue(number:$n){ id } }
      }"""
    return gql(q, owner=owner, repo=repo.name, n=num)["repository"]["issue"]["id"]

# ----------------------------------------------------------- upsert file
def upsert(path: str, message: str, content: str, branch="main"):
    try:
        cur = repo.get_contents(path, ref=branch)
        repo.update_file(path, message, content, cur.sha, branch=branch)
    except GithubException as e:
        if e.status == 404:
            repo.create_file(path, message, content, branch=branch)
        else:
            raise

# ----------------------------------------------------------- 1) board & issues
pid = project_v2_id()

ISSUES = [
    ("Epic : Bootstrap infrastructure",
     "- [ ] Stocker OPENAI_API_KEY dans GitHub Secrets\n"
     "- [ ] Générer la clé ServiceAccount GCP\n"
     "- [ ] Créer projet Supabase `jarvys_dev_mem`\n"
     "- [ ] Ajouter workflow `ci.yml`"),
    ("Epic : Core tools",
     "- [ ] Implémenter `github_create_issue`\n"
     "- [ ] Implémenter `memory_search`\n"
     "- [ ] Tests unitaires tools"),
    ("Epic : Persona & données Yann",
     "- [ ] Export PDF LinkedIn\n"
     "- [ ] Script `load_linkedin.py` ➜ Supabase")
]

open_titles = {i.title for i in repo.get_issues(state="open")}
for title, body in ISSUES:
    if title in open_titles:               # évite doublon
        print(f"⚠️  Issue « {title} » déjà ouverte — saut")
        continue
    issue = repo.create_issue(title, body)
    node  = getattr(issue, "node_id", None) or issue_node_id(issue.number)
    project_add_issue(pid, node)
    print(f"✅  Issue créée : #{issue.number} – {title}")

# ----------------------------------------------------------- 2) CI workflow
ci = textwrap.dedent("""\
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
          - run: poetry run pytest""")
upsert(".github/workflows/ci.yml", "Add/Update CI workflow", ci)

# ----------------------------------------------------------- 3) devcontainer
devc = textwrap.dedent("""\
{
  "name": "jarvys_dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "pip install --no-cache-dir poetry PyGithub==2.4.0 && poetry config virtualenvs.create false"
}""")
upsert(".devcontainer/devcontainer.json", "Add/Update devcontainer", devc)

# ----------------------------------------------------------- 4) tool stub
stub = 'def github_create_issue(title:str, body:str=""):\n    """TODO"""'
upsert("src/jarvys_dev/tools/github_tools.py", "Add/Update tool stub", stub)

print("🎉  Bootstrap terminé — script relançable à l’infini.")
# --------------------------------------------------------------------- EOF
