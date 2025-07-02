#!/usr/bin/env python3
"""
Bootstrap JARVYS_DEV : crée un Project v2, les issues initiales,
un workflow CI, un devcontainer et les stubs de tools.

Exécution :
    $ python bootstrap_jarvys_dev.py
Variables d’environnement attendues :
    GH_TOKEN, GH_REPO, SUPABASE_URL, SUPABASE_KEY,
    GCP_SA_JSON, OPENAI_API_KEY, GEMINI_API_KEY
"""

# ────────── dépendances ──────────
import os, sys, textwrap, pathlib, subprocess
try:
    from github import Github
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "PyGithub>=2.4.0"])
    from github import Github
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# ────────── vérif env ──────────
env = {k: os.getenv(k) for k in (
    "GH_TOKEN","GH_REPO","SUPABASE_URL","SUPABASE_KEY",
    "GCP_SA_JSON","OPENAI_API_KEY","GEMINI_API_KEY"
)}
missing = [k for k,v in env.items() if not v]
if missing:
    sys.exit(f"❌  Variables manquantes : {', '.join(missing)}")

gh_token, gh_repo_id = env["GH_TOKEN"], env["GH_REPO"]
gh   = Github(gh_token)
repo = gh.get_repo(gh_repo_id)

# ────────── helpers GraphQL ──────────
GQL = "https://api.github.com/graphql"
HDR = {"Authorization": f"bearer {gh_token}", "Content-Type":"application/json"}
def graphql(query:str, **vars):
    r = requests.post(GQL, headers=HDR, json={"query": textwrap.dedent(query), "variables": vars}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]

# ────────── Project v2 ──────────
PROJECT_TITLE = "JARVYS_DEV Roadmap"

def get_or_create_project_v2(owner_login:str, title:str)->str:
    # 1) user ?
    q_user = """
      query($login:String!){
        user(login:$login){
          id
          projectsV2(first:100){ nodes{ id title url } }
        }
      }"""
    d = graphql(q_user, login=owner_login)
    if d.get("user"):
        for n in d["user"]["projectsV2"]["nodes"]:
            if n["title"] == title:
                print(f"ℹ️  Project déjà présent : {n['url']}")
                return n["id"]
        owner_id = d["user"]["id"]
    else:
        # 2) org
        q_org = """
          query($login:String!){
            organization(login:$login){
              id
              projectsV2(first:100){ nodes{ id title url } }
            }
          }"""
        d = graphql(q_org, login=owner_login)
        if not d.get("organization"):
            raise RuntimeError(f"Aucun compte GitHub '{owner_login}' trouvé.")
        for n in d["organization"]["projectsV2"]["nodes"]:
            if n["title"] == title:
                print(f"ℹ️  Project déjà présent : {n['url']}")
                return n["id"]
        owner_id = d["organization"]["id"]

    # 3) create
    mut = """
      mutation($owner:ID!,$title:String!){
        createProjectV2(input:{ownerId:$owner,title:$title}){
          projectV2{ id url }
        }
      }"""
    proj = graphql(mut, owner=owner_id, title=title)["createProjectV2"]["projectV2"]
    print(f"✅  Project créé : {proj['url']}")
    return proj["id"]

def add_issue_to_project(project_id:str, node_id:str):
    mut = """
      mutation($proj:ID!,$content:ID!){
        addProjectV2ItemById(input:{projectId:$proj, contentId:$content}){ item{ id } }
      }"""
    graphql(mut, proj=project_id, content=node_id)

def issue_node_id(owner:str, repo_name:str, number:int)->str:
    q = """
      query($owner:String!,$name:String!,$num:Int!){
        repository(owner:$owner,name:$name){
          issue(number:$num){ id }
        }
      }"""
    d = graphql(q, owner=owner, name=repo_name, num=number)
    return d["repository"]["issue"]["id"]

owner_login   = repo.owner.login
project_id    = get_or_create_project_v2(owner_login, PROJECT_TITLE)

# ────────── Issues initiales ──────────
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
    # Récupération robuste du node‑ID
    node_id = getattr(issue, "node_id", None)
    if not node_id:
        node_id = issue_node_id(owner_login, repo.name, issue.number)
    add_issue_to_project(project_id, node_id)
    print(f"✅  Issue créée : #{issue.number} – {title}")

# ────────── Workflow CI ──────────
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

# ────────── Devcontainer ──────────
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
}""")
(devc_dir/"devcontainer.json").write_text(devc_json)
repo.create_file(".devcontainer/devcontainer.json", "Add devcontainer", devc_json, branch="main")

# ────────── Tool stubs ──────────
pkg_dir = pathlib.Path("src/jarvys_dev/tools"); pkg_dir.mkdir(parents=True, exist_ok=True)
(pkg_dir/"__init__.py").write_text("")
tool_stub = textwrap.dedent("""\
    def github_create_issue(title:str, body:str=\"\"):
        \"\"\"TODO : créer une issue via l’API GitHub\"\"\"
        raise NotImplementedError
""")
(pkg_dir/"github_tools.py").write_text(tool_stub)
repo.create_file("src/jarvys_dev/tools/github_tools.py", "Add tool stub", tool_stub, branch="main")

print("🎉  Bootstrap terminé – poussez et ouvrez une PR si besoin.")
