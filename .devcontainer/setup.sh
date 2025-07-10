#!/usr/bin/env bash
set -euo pipefail

################################################################################
# 0. Variables & fonctions utilitaires
################################################################################
export DEBIAN_FRONTEND=noninteractive
export CLOUDSDK_CORE_DISABLE_PROMPTS=1   # Plus aucun prompt gcloud
NVM_DIR=/usr/local/share/nvm             # Chemin utilisé par la feature Node
SUPABASE_VERSION=${SUPABASE_VERSION:-1.179.1}   # Dernière version stable

silent_apt_update() { sudo apt-get update -qq; }
apt_install()      { silent_apt_update && sudo apt-get install -yqq "$@"; }

have_cmd() { command -v "$1" &>/dev/null; }

################################################################################
# 1. Dépendances système de base
################################################################################
echo "▶︎ Installation des dépendances APT de base"
apt_install curl gnupg ca-certificates apt-transport-https jq tar gzip

################################################################################
# 2. Google Cloud CLI
################################################################################
if ! have_cmd gcloud; then
  echo "▶︎ Installation Google Cloud CLI"
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
https://packages.cloud.google.com/apt cloud-sdk main" \
      | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
      | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  apt_install google-cloud-cli
fi

if [[ -n "${GCP_SA_JSON:-}" ]]; then
  echo "▶︎ Authentification GCP (service account)"
  SA_FILE=$(mktemp)
  echo "${GCP_SA_JSON}" > "${SA_FILE}"
  gcloud auth activate-service-account --key-file="${SA_FILE}" --quiet
  PROJECT_ID=$(jq -r '.project_id' "${SA_FILE}")
  gcloud config set project "${PROJECT_ID}" --quiet || true
  rm -f "${SA_FILE}"

  echo "▶︎ Activation des APIs (Cloud Resource Manager + requises)"
  gcloud services enable \
    cloudresourcemanager.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    iamcredentials.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    --quiet || true
fi

################################################################################
# 3. Node (chemin garanti) & Supabase CLI
################################################################################
# ––––– Assurer que le binaire npm est dans le PATH même dans ce shell non‑login ––––– #
if [[ -s "${NVM_DIR}/nvm.sh" ]]; then
  source "${NVM_DIR}/nvm.sh"
elif [[ -d "${NVM_DIR}" ]]; then
  # Ajout dynamique de tous les binaires Node installés par la feature
  for vdir in "${NVM_DIR}/versions/node"/*/bin; do
    [[ -d "$vdir" ]] && PATH="$vdir:$PATH"
  done
  export PATH
fi

install_supabase() {
  echo "▶︎ Installation Supabase CLI (binary ${SUPABASE_VERSION})"
  URL="https://github.com/supabase/cli/releases/download/v${SUPABASE_VERSION}/supabase_${SUPABASE_VERSION}_linux_amd64.tar.gz"
  TMP_DIR=$(mktemp -d)
  curl -fsSL "$URL" | tar -xz -C "$TMP_DIR"
  sudo install -m 0755 "$TMP_DIR/supabase" /usr/local/bin/supabase
  rm -rf "$TMP_DIR"
}

if have_cmd supabase; then
  echo "▶︎ Supabase CLI déjà présent : $(supabase --version)"
elif have_cmd npm; then
  echo "▶︎ Installation Supabase CLI via npm"
  sudo npm install -g --silent supabase || install_supabase
else
  # npm absent : on installe la version binaire auto‑contenue
  install_supabase
fi

################################################################################
# 4. Poetry + dépendances Python
################################################################################
if ! have_cmd poetry; then
  echo "▶︎ Installation Poetry"
  python -m pip install --no-cache-dir --quiet poetry
fi

echo "▶︎ Installation dépendances Python (poetry install --with dev)"
poetry install --with dev --no-root --no-interaction

################################################################################
# 5. Hooks git pré‑commit
################################################################################
echo "▶︎ Installation hooks pre‑commit"
poetry run pre-commit install --install-hooks --overwrite

echo -e "\n✅  Environnement prêt !"
