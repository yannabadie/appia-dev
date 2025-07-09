#!/usr/bin/env bash
set -euo pipefail

echo "▶︎ Mise à jour APT & dépendances de base"
sudo apt-get update -y
sudo apt-get install -y curl gnupg lsb-release jq

###############################################################################
# 1. Google Cloud CLI   (installation manuelle, stable et hors feature broken)
###############################################################################
if ! command -v gcloud >/dev/null 2>&1; then
  echo "▶︎ Installation Google Cloud CLI"
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
https://packages.cloud.google.com/apt cloud-sdk main" \
    | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | sudo tee /usr/share/keyrings/cloud.google.gpg >/dev/null
  sudo apt-get update -y && sudo apt-get install -y google-cloud-cli
fi

###############################################################################
# 2. Authentification service‑account (facultatif)
###############################################################################
if [[ -n "${GCP_SA_JSON:-}" ]]; then
  echo "▶︎ Authentification GCP via service‑account"
  printf '%s\n' "${GCP_SA_JSON}" > /tmp/sa.json
  gcloud auth activate-service-account --key-file=/tmp/sa.json
  PROJECT_ID=$(jq -r '.project_id' /tmp/sa.json)
  gcloud config set project "${PROJECT_ID}"
  rm /tmp/sa.json
fi

###############################################################################
# 3. Supabase CLI
###############################################################################
if ! command -v supabase >/dev/null 2>&1; then
  echo "▶︎ Installation Supabase CLI"
  npm install -g supabase
fi

###############################################################################
# 4. Poetry + dépendances Python du projet
###############################################################################
if ! command -v poetry >/dev/null 2>&1; then
  echo "▶︎ Installation Poetry"
  pip install --no-cache-dir poetry
fi

# Crée / met à jour l’environnement virtuel dans ~/.cache/pypoetry/virtualenvs
echo "▶︎ Installation dépendances (poetry install --with dev)"
poetry install --with dev

###############################################################################
# 5. Hooks git pré‑commit
###############################################################################
echo "▶︎ Installation hooks pre‑commit"
poetry run pre-commit install

echo "✅  Environnement prêt !"
