#!/usr/bin/env bash
set -euo pipefail

################################################################################
# 1. Pré‑requis système
################################################################################
export DEBIAN_FRONTEND=noninteractive
export CLOUDSDK_CORE_DISABLE_PROMPTS=1   # Désactive tous les prompts gcloud

echo "▶︎ Installation des dépendances APT de base"
apt-get update -qq \
  && apt-get install -yqq curl gnupg ca-certificates apt-transport-https jq

################################################################################
# 2. Google Cloud CLI
################################################################################
echo "▶︎ Installation Google Cloud CLI"
if ! command -v gcloud &>/dev/null; then
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee /etc/apt/sources.list.d/google-cloud-sdk.list
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  apt-get update -qq && apt-get install -yqq google-cloud-cli
fi

echo "▶︎ Authentification GCP (service account)"
if [[ -n "${GCP_SA_JSON:-}" ]]; then
  SA_FILE="$(mktemp)"
  echo "${GCP_SA_JSON}" > "${SA_FILE}"
  gcloud auth activate-service-account --key-file="${SA_FILE}" --quiet
  PROJECT_ID="$(jq -r '.project_id' "${SA_FILE}")"
  gcloud config set project "${PROJECT_ID}" --quiet || true
  rm -f "${SA_FILE}"

  ##########################################################################
  # 2.3 Activation (silencieuse) des APIs nécessaires
  ##########################################################################
  echo "▶︎ Activation des APIs GCP essentielles"
  gcloud services enable \
    cloudresourcemanager.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    iam.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --quiet || true
fi

################################################################################
# 3. Supabase CLI
################################################################################
echo "▶︎ Installation Supabase CLI"
if ! command -v supabase &>/dev/null; then
  npm install -g --silent supabase
fi

################################################################################
# 4. Poetry + dépendances Python
################################################################################
echo "▶︎ Installation Poetry"
if ! command -v poetry &>/dev/null; then
  python -m pip install --no-cache-dir --quiet poetry
fi

echo "▶︎ Installation dépendances (poetry install --with dev)"
poetry install --with dev --no-root --no-interaction

################################################################################
# 5. Hooks git pré‑commit
################################################################################
echo "▶︎ Installation hooks pre‑commit"
poetry run pre-commit install --install-hooks --overwrite

echo -e "\n✅  Environnement prêt !"
