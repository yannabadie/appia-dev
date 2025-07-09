#!/usr/bin/env bash
set -euo pipefail

echo "▶︎ System packages & helpers"
sudo apt-get update -y
sudo apt-get install -y curl jq gnupg build-essential

###############################################################################
# Google Cloud CLI – installation manuelle (la Feature posait problème)
###############################################################################
if ! command -v gcloud &>/dev/null; then
  echo "▶︎ Installing Google Cloud SDK"
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
https://packages.cloud.google.com/apt cloud-sdk main" \
  | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
  curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg \
  | sudo tee /usr/share/keyrings/cloud.google.gpg >/dev/null
  sudo apt-get update -y && sudo apt-get install -y google-cloud-cli
fi

# Authentification service account (optionnelle)
if [[ -n "${GCP_SA_JSON:-}" ]]; then
  echo "▶︎ gcloud auth activate‑service‑account"
  echo "${GCP_SA_JSON}" > /tmp/sa.json
  gcloud auth activate-service-account --key-file=/tmp/sa.json --quiet
  PROJECT_ID=$(jq -r '.project_id' /tmp/sa.json)
  gcloud config set project "${PROJECT_ID}"
  rm -f /tmp/sa.json
fi

###############################################################################
# Supabase CLI
###############################################################################
if ! command -v supabase &>/dev/null; then
  echo "▶︎ Installing Supabase CLI"
  npm install -g supabase
fi

###############################################################################
# Poetry + dépendances projet
###############################################################################
if ! command -v poetry &>/dev/null; then
  echo "▶︎ Installing Poetry"
  pip install --no-cache-dir poetry
fi

echo "▶︎ Installing Python deps via Poetry"
poetry install --with dev

###############################################################################
# Pré‑commit
###############################################################################
echo "▶︎ Installing git hooks"
poetry run pre-commit install

echo "✅  Setup terminé – happy coding!"
