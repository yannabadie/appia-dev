#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# Helper : exécute une commande en root (sudo) quel que soit l’utilisateur
###############################################################################
as_root() {
  if [ "$(id -u)" -eq 0 ]; then
    "$@"
  else
    sudo -E bash -c "$*"
  fi
}

###############################################################################
# 0. Variables d’environnement – aucun prompt pendant le provisionning
###############################################################################
export DEBIAN_FRONTEND=noninteractive
export CLOUDSDK_CORE_DISABLE_PROMPTS=1   # gcloud jamais interactif
export PATH="$PATH:/usr/local/bin"       # npm/pip global installs

###############################################################################
# 1. Dépendances APT de base
###############################################################################
echo "▶︎ Installation des dépendances APT de base"
as_root mkdir -p /var/lib/apt/lists/partial           # évite l’erreur « missing dir »
as_root apt-get update -qq
as_root apt-get install -yqq curl gnupg ca-certificates apt-transport-https jq

###############################################################################
# 2. Google Cloud CLI
###############################################################################
echo "▶︎ Installation Google Cloud CLI"
if ! command -v gcloud >/dev/null 2>&1; then
  # Ajout du dépôt (clé dans un keyring dédié)
  if [ ! -f /usr/share/keyrings/cloud.google.gpg ]; then
    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
      | as_root gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  fi

  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
https://packages.cloud.google.com/apt cloud-sdk main" \
    | as_root tee /etc/apt/sources.list.d/google-cloud-sdk.list >/dev/null

  as_root apt-get update -qq
  as_root apt-get install -yqq google-cloud-cli
fi

###############################################################################
# 2.b Authentification + activation d’APIs
###############################################################################
if [[ -n "${GCP_SA_JSON:-}" ]]; then
  echo "▶︎ Authentification GCP (service account)"
  SA_FILE="$(mktemp)"
  echo "${GCP_SA_JSON}" > "${SA_FILE}"

  gcloud auth activate-service-account --key-file="${SA_FILE}" --quiet
  PROJECT_ID=$(jq -r '.project_id' "${SA_FILE}")
  gcloud config set project "${PROJECT_ID}" --quiet || true

  # APIs indispensables (ajoutez/retirez au besoin)
  APIS=(
    cloudresourcemanager.googleapis.com
    iam.googleapis.com
    iamcredentials.googleapis.com
    artifactregistry.googleapis.com
    run.googleapis.com
    secretmanager.googleapis.com
    sqladmin.googleapis.com
  )
  echo "▶︎ Activation des APIs (${#APIS[@]})"
  for API in "${APIS[@]}"; do
    gcloud services enable "${API}" --quiet || true
  done

  rm -f "${SA_FILE}"
fi

###############################################################################
# 3. Supabase CLI (global, silencieux)
###############################################################################
echo "▶︎ Installation Supabase CLI"
if ! command -v supabase >/dev/null 2>&1; then
  as_root npm install -g --silent supabase
fi

###############################################################################
# 4. Poetry + dépendances Python
###############################################################################
echo "▶︎ Installation Poetry"
if ! command -v poetry >/dev/null 2>&1; then
  as_root python -m pip install --no-cache-dir --quiet poetry
fi

echo "▶︎ Installation dépendances (poetry install --with dev)"
poetry install --with dev --no-root --no-interaction

###############################################################################
# 5. Hooks git pré‑commit
###############################################################################
echo "▶︎ Installation hooks pre‑commit"
poetry run pre-commit install --install-hooks --overwrite

echo -e "\n\033[1;32m✅  Environnement prêt !\033[0m"
