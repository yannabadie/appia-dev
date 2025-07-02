#!/usr/bin/env python3
"""
Bootstrap JARVYS_DEV: crée Kanban, issues, CI, devcontainer.
Exécutez:
    $ python bootstrap_jarvys_dev.py
Variables d'environnement attendues :
    GH_TOKEN         : Personal Access Token GitHub
    GH_REPO          : org/repo  (ex : yannabadie/appia-dev)
    SUPABASE_URL     : https://xxxx.supabase.co
    SUPABASE_KEY     : service_role ou anon
    GCP_SA_JSON      : chemin local vers la clé JSON
    OPENAI_API_KEY   : ...
    GEMINI_API_KEY   : ...
"""
try:
    from github import Github
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyGithub>=2.4.0"])
    from github import Github

import os, json, textwrap, subprocess, base64, pathlib, sys
from datetime import datetime
from github import Github

### 1) -------------------  Vérifications préalables  ----------------------
env = {k: os.getenv(k) for k in [
    "GH_TOKEN","GH_REPO","SUPABASE_URL","SUPABASE_KEY",
    "GCP_SA_JSON","OPENAI_API_KEY","GEMINI_API_KEY"
]}
missing = [k for k,v in env.items() if not v]
if missing:
    sys.exit(f"❌ Manquent variables d'environnement : {', '.join(missing)}")

g = Github(env["GH_TOKEN"])
repo = g.get_repo(env["GH_REPO"])

### 2) -------------------  Board Kanban Projects v2  ----------------------
project_name = "JARVYS_DEV Roadmap"
projects = list(repo.get_projects())  # classic projects
proj = next((p for p in projects if p.name==project_name), None)
if not proj:
    proj = repo.create_project(project_name, body="Roadmap auto‑générée")
    print(f"✅ Projet créé : {proj.html_url}")
columns = {c.name:c for c in proj.get_columns()}
for col in ["Backlog","En cours","Revue","Terminé"]:
    columns.setdefault(col, proj.create_column(col))

### 3) -------------------  Issues initiales -------------------------------
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
    columns["Backlog"].create_card(content_id=issue.id, content_type="Issue")
    print(f"✅ Issue créée : #{issue.number} {title}")

### 4) -------------------  CI workflow ------------------------------------
ci_path = pathlib.Path(".github/workflows/ci.yml")
ci_path.parent.mkdir(parents=True, exist_ok=True)
ci_path.write_text(textwrap.dedent(f"""\
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

### 5) -------------------  Devcontainer -----------------------------------
(pathlib.Path(".devcontainer")/ "devcontainer.json").write_text(textwrap.dedent("""\
{
  "name": "jarvys_dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "pip install poetry pre-commit && poetry install && pre-commit install",
  "forwardPorts": [54321],
  "customizations": { "vscode": { "settings": { "python.defaultInterpreterPath": "/usr/local/bin/python" } } }
}
"""))
repo.create_file(".devcontainer/devcontainer.json", "Add devcontainer", open(".devcontainer/devcontainer.json").read(), branch="main")

### 6) -------------------  Stubs tools ------------------------------------
pkg_dir = pathlib.Path("src/jarvys_dev/tools"); pkg_dir.mkdir(parents=True, exist_ok=True)
(pkg_dir/"__init__.py").write_text("")
(pkg_dir/"github_tools.py").write_text(textwrap.dedent("""\
def github_create_issue(title:str, body:str=""):
    '''TODO: create issue via GitHub API'''
    raise NotImplementedError
"""))

repo.create_file("src/jarvys_dev/tools/github_tools.py",
                 "Add tool stub", open("src/jarvys_dev/tools/github_tools.py").read(), branch="main")

print("🎉  Bootstrap terminé – poussez et ouvrez une PR si besoin.")
