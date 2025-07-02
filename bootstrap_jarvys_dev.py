#!/usr/bin/env python3
"""
Bootstrap JARVYS_DEV : crée un Project v2 GitHub, les issues initiales,
un workflow CI, un devcontainer et les stubs de tools.

Exécution :
    $ python bootstrap_jarvys_dev.py

Variables d’environnement attendues :
    GH_TOKEN        : Personal Access Token GitHub (scopes repo, workflow, project)
    GH_REPO         : org/repo (ex. yannabadie/appia-dev)
    SUPABASE_URL    : https://xxxx.supabase.co
    SUPABASE_KEY    : service_role ou anon
    GCP_SA_JSON     : chemin local vers la clé JSON
    OPENAI_API_KEY  : ...
    GEMINI_API_KEY  : ...
"""

# ────────────────────────── dépendances Python ───────────────────────────────
import os, sys, textwrap, pathlib, subprocess, json
try:
    from github import Github
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "PyGithub>=2.4.0"]
    )
    from github import Github

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# ────────────────────────── vérif variables d’env. ───────────────────────────
env = {k: os.getenv(k) for k in (
    "GH_TOKEN", "GH_REPO", "SUPABASE_URL", "SUPABASE_KEY",
    "GCP_SA_JSON", "OPENAI_API_KEY", "GEMINI_API_KEY"
)}
missing = [k for k, v in env.items() if not v]
if missing:
    sys.exit(f"❌  Variables d’environnement manquantes : {', '.join(missing)}")

gh_token   = env["GH_TOKEN"]
gh_repo_id = env["GH_REPO"]

gh  = Github(gh_token)
repo = gh.get_repo(gh_repo_id)

# ──────────────────────── helpers GraphQL « requests » ───────────────────────
GQL_ENDPOINT = "https://api.github.com/graphql"
HEADERS = {
    "Authorization": f"bearer {gh_token}",
    "Content-Type": "application/json"
}

def graphql(query: str, **variables):
    """Appelle l’API GraphQL GitHub et retourne les données JSON."""
    payload = {"query": textwrap.dedent(query), "variables": variables}
    r = requests.post(GQL_ENDPOINT, headers=HEADERS, json=payload, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"GraphQL HTTP {r.status_code}: {r.text}")
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]

# ───────────────────── Project v2 (nouvelle expérience) ─────────────────────
PROJECT_TITLE = "JARVYS_DEV Roadmap"

def owner_node_id_and_type(owner_login:str):
    q = """
      query($login:String!){
        user(login:$login){ id }
        organization(login:$login){ id }
      }
    """
    d = graphql(q, login=owner_login)
    if d["user"]:
        return d["user"]["id"], "user"
    if d["organization"]:
        return d["organization"]["id"], "org"
    raise RuntimeError(f"Owner {owner_login} introuvable.")

def get_or_create_project_v2(owner_login:str, title:str)->str:
    # 1) cherche
    search = """
      query($login:String!){
        user(login:$login){ projectsV2(first:100){ nodes{ id title url } } }
        organization(login:$login){ projectsV2(first:100){ nodes{ id title url } } }
      }
    """
    nodes = (graphql(search, login=owner_login)["user"]
             or graphql(search, login=owner_login)["organization"])["projectsV2"]["nodes"]
    for n in nodes:
        if n["title"] == title:
            print(f"ℹ️  Project déjà présent : {n['url']}")
            return n["id"]

    # 2) crée
    owner_id, _ = owner_node_id_and_type(owner_login)
    create = """
      mutation($owner:ID!,$title:String!){
        createProjectV2(input:{ownerId:$owner,title:$title}){
          projectV2{ id url }
        }
      }
    """
    proj = graphql(create, owner=owner_id, title=title)["createProjectV2"]["projectV2"]
    print(f"✅  Project créé : {proj['url']}")
    return proj["id"]

def add_issue_to_project(project_id:str, issue_node_id:str):
    q = """
      mutation($proj:ID!,$content:ID!){
        addProjectV2ItemById(input:{projectId:$proj,contentId:$content}){ item{ id } }
      }
    """
    graphql(q, proj=project_id, content=issue_node_id)

owner_login = repo.owner.login
project_id  = get_or_create_project_v2(owner_login, PROJECT_TITLE)

# ───────────────────────────── issues initiales ──────────────────────────────
issues_spec = [
    ("Epic : Bootstrap infrastructure",
     "- [ ] Chiffrer l’API‑key OpenAI et la stocker dans GitHub Secrets\n"
     "- [ ] Générer et stocker le JSON Service Account GCP\n"
     "- [ ] Créer projet Supabase `jarvys_dev_mem`\n"
     "- [ ] Ajouter GitHub Action `ci.yml` (lint+tests)"),
    ("Epic : Core tools",
     "- [ ] Implémenter `tool_github_create_issue`\n"
     "- [ ] Implémenter `tool_memory_search`\n"
     "- [ ] Rédiger tests unitaires pour chaque tool"),
    ("Epic : Persona & données Yann",
     "- [ ] Exporter profil LinkedIn en PDF/HTML\n"
     "- [ ] Écrire script `load_linkedin.py` (BeautifulSoup ➜ embedding ➜ Supabase)")
]

for title, body in issues_spec:
    issue = repo.create_issue(title, body)
    add_issue_to_project(project_id, issue.node_id)
    print(f"✅  Issue créée : #{issue.number} – {title}")

# ───────────────────────────── workflow CI ───────────────────────────────────
ci_path = pathlib.Path(".github/workflows/ci.yml")
ci_path.parent.mkdir(parents=True, exist_ok=True)
ci_path.write_text(textwrap.dedent("""\
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
"""))
repo.create_file(str(ci_path), "Add CI workflow", ci_path.read_text(), branch="main")

# ───────────────────────────── devcontainer ─────────────────────────────────
devc_dir = pathlib.Path(".devcontainer"); devc_dir.mkdir(exist_ok=True)
devc_json = textwrap.dedent("""\
{
  "name": "jarvys_dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "pip install --no-cache-dir poetry PyGithub==2.4.0 && poetry config virtualenvs.create false",
  "forwardPorts": [54321]
}
""")
(devc_dir / "devcontainer.json").write_text(devc_json)
repo.create_file(
    ".devcontainer/devcontainer.json", "Add devcontainer", devc_json, branch="main"
)

# ─────────────────────────── stubs des tools ────────────────────────────────
pkg_dir = pathlib.Path("src/jarvys_dev/tools"); pkg_dir.mkdir(parents=True, exist_ok=True)
(pkg_dir / "__init__.py").write_text("")
tool_stub = textwrap.dedent("""\
    def github_create_issue(title: str, body: str = ""):
        \"\"\"TODO : créer une issue via l’API GitHub\"\"\"
        raise NotImplementedError
""")
(pkg_dir / "github_tools.py").write_text(tool_stub)
repo.create_file(
    "src/jarvys_dev/tools/github_tools.py", "Add tool stub", tool_stub, branch="main"
)

print("🎉  Bootstrap terminé – poussez et ouvrez une PR si besoin.")
