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
# ──────────────────────────────────────────────────────────────────────────────
# Dépendance PyGithub : installation « silencieuse » si absente
try:
    from github import Github
except ImportError:
    import subprocess, sys
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "PyGithub>=2.4.0", "--quiet"]
    )
    from github import Github

import os, textwrap, pathlib, sys

# ═══════════════ 1) Vérifications préalables ═════════════════════════════════
env = {k: os.getenv(k) for k in (
    "GH_TOKEN", "GH_REPO", "SUPABASE_URL", "SUPABASE_KEY",
    "GCP_SA_JSON", "OPENAI_API_KEY", "GEMINI_API_KEY"
)}
missing = [k for k, v in env.items() if not v]
if missing:
    sys.exit(f"❌  Variables d’environnement manquantes : {', '.join(missing)}")

gh = Github(env["GH_TOKEN"])
repo = gh.get_repo(env["GH_REPO"])

# ═══════════════ 2) Project v2 (GraphQL) ═════════════════════════════════════
PROJECT_TITLE = "JARVYS_DEV Roadmap"

def _graphql(query: str, **variables):
    """Aide pour invoquer l’API GraphQL de GitHub via PyGithub."""
    return gh.graphql(textwrap.dedent(query), **variables)

def _owner_node_and_type(owner_login: str):
    """Renvoie (node_id, kind) où kind ∈ {'user','org'}."""
    q = """
        query ($login:String!) {
          user(login:$login) { id }
          organization(login:$login) { id }
        }
    """
    data = _graphql(q, login=owner_login)
    if data["user"]:
        return data["user"]["id"], "user"
    if data["organization"]:
        return data["organization"]["id"], "org"
    raise RuntimeError(f"⚠️  Impossible de récupérer l’owner {owner_login}")

def get_or_create_project_v2(owner_login: str, title: str) -> str:
    """Retourne l’ID GraphQL du Project v2, le crée sinon."""
    # 1) Recherche
    search_q = """
        query ($login:String!, $first:Int!) {
          user(login:$login) {
            projectsV2(first:$first) { nodes { id title } }
          }
          organization(login:$login) {
            projectsV2(first:$first) { nodes { id title } }
          }
        }
    """
    data = _graphql(search_q, login=owner_login, first=100)
    nodes = (data["user"] or data["organization"])["projectsV2"]["nodes"]
    for n in nodes:
        if n["title"] == title:
            print(f"ℹ️  Project déjà présent : {title}")
            return n["id"]

    # 2) Création
    owner_id, _ = _owner_node_and_type(owner_login)
    create_q = """
        mutation ($ownerId:ID!, $title:String!) {
          createProjectV2(input:{ownerId:$ownerId, title:$title}) {
            projectV2 { id url }
          }
        }
    """
    created = _graphql(create_q, ownerId=owner_id, title=title)["createProjectV2"]["projectV2"]
    print(f"✅  Project créé : {created['url']}")
    return created["id"]

def add_issue_to_project(project_id: str, issue_node_id: str):
    """Ajoute une issue (#) dans la colonne ‘Todo’ du Project v2."""
    q = """
        mutation ($proj:ID!, $content:ID!) {
          addProjectV2ItemById(input:{projectId:$proj, contentId:$content}) {
            item { id }
          }
        }
    """
    _graphql(q, proj=project_id, content=issue_node_id)

owner_login = repo.owner.login
project_id = get_or_create_project_v2(owner_login, PROJECT_TITLE)

# ═══════════════ 3) Issues initiales ════════════════════════════════════════
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

# ═══════════════ 4) Workflow CI ═════════════════════════════════════════════
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

# ═══════════════ 5) Devcontainer ═══════════════════════════════════════════
devc_dir = pathlib.Path(".devcontainer"); devc_dir.mkdir(exist_ok=True)
(devc_dir / "devcontainer.json").write_text(textwrap.dedent("""\
{
  "name": "jarvys_dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "pip install --no-cache-dir poetry PyGithub==2.4.0 && poetry config virtualenvs.create false",
  "forwardPorts": [54321],
  "customizations": {
    "vscode": {
      "settings": { "python.defaultInterpreterPath": "/usr/local/bin/python" }
    }
  }
}
"""))
repo.create_file(
    ".devcontainer/devcontainer.json",
    "Add devcontainer",
    (devc_dir / "devcontainer.json").read_text(),
    branch="main"
)

# ═══════════════ 6) Stubs des tools ════════════════════════════════════════
pkg_dir = pathlib.Path("src/jarvys_dev/tools"); pkg_dir.mkdir(parents=True, exist_ok=True)
(pkg_dir / "__init__.py").write_text("")
tool_stub = textwrap.dedent("""\
    def github_create_issue(title: str, body: str = ""):
        \"\"\"TODO : créer une issue via l’API GitHub\"\"\"
        raise NotImplementedError
""")
(pkg_dir / "github_tools.py").write_text(tool_stub)

repo.create_file(
    "src/jarvys_dev/tools/github_tools.py",
    "Add tool stub",
    tool_stub,
    branch="main"
)

print("🎉  Bootstrap terminé – poussez et ouvrez une PR si besoin.")
