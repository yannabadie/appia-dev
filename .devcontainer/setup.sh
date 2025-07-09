#!/usr/bin/env bash
set -euo pipefail

echo "▶︎ Installation des pré‑requis système"
sudo apt-get update -y \
  && sudo apt-get install -y --no-install-recommends \
       curl gnupg ca-certificates lsb-release jq

###############################################################################
# 1. Google Cloud CLI
###############################################################################
if ! command -v gcloud &>/dev/null; then
  echo "▶︎ Installation Google Cloud CLI"

  # ‑‑ clé officielle (ID C0BA 5CE6 DC63 15A3) dans un keyring dédié
  GCLOUD_KEYRING=/usr/share/keyrings/google-cloud.gpg
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
       sudo gpg --dearmor -o "$GCLOUD_KEYRING"

  # ‑‑ dépôt signé par cette clé
  echo "deb [signed-by=$GCLOUD_KEYRING] https://packages.cloud.google.com/apt cloud-sdk main" | \
       sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list

  sudo apt-get update -y && sudo apt-get install -y google-cloud-cli
fi

# Authentification éventuelle via compte de service
if [[ -n "${GCP_SA_JSON:-}" ]]; then
  echo "▶︎ Authentification GCP (service account)"
  echo "${GCP_SA_JSON}" > /tmp/sa.json
  gcloud auth activate-service-account --key-file=/tmp/sa.json
  PROJECT_ID=$(jq -r '.project_id' /tmp/sa.json)
  gcloud config set project "${PROJECT_ID}"
  rm /tmp/sa.json
fi

###############################################################################
# 2. Supabase CLI
###############################################################################
if ! command -v supabase &>/dev/null; then
  echo "▶︎ Installation Supabase CLI"
  npm install -g supabase
fi

###############################################################################
# 3. Poetry + dépendances Python
###############################################################################
if ! command -v poetry &>/dev/null; then
  echo "▶︎ Installation Poetry"
  # pip est déjà présent dans l’image Python officielle
  pip install --no-cache-dir --break-system-packages poetry
fi

echo "▶︎ Installation dépendances (poetry install --with dev)"
poetry install --with dev

###############################################################################
# 4. Hooks git pré‑commit
###############################################################################
echo "▶︎ Installation hooks pré‑commit"
poetry run pre-commit install

echo -e '\n✅  Environnement prêt !'
