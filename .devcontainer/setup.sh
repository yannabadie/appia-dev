#!/usr/bin/env bash
set -euo pipefail

echo -e "\n\033[1;34m▶︎ Installing system prerequisites\033[0m"
sudo apt-get update -qq
sudo apt-get install -y -qq \
     curl gnupg ca-certificates apt-transport-https jq

###############################################################################
# 1. Google Cloud SDK (APT repo, modern keyring flow)
###############################################################################
if ! command -v gcloud &>/dev/null; then
  echo -e "\n\033[1;34m▶︎ Installing Google Cloud CLI\033[0m"
  sudo install -d -m 0755 /etc/apt/keyrings
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg |
       sudo tee /etc/apt/keyrings/google-cloud.gpg >/dev/null
  echo \
    "deb [signed-by=/etc/apt/keyrings/google-cloud.gpg] \
     https://packages.cloud.google.com/apt cloud-sdk main" |
     sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list >/dev/null

  sudo apt-get update -qq
  sudo apt-get install -y google-cloud-cli
fi

# Optional: service‑account login (skipped on CI to avoid secrets bleed)
if [[ -n "${GCP_SA_JSON:-}" && ! -f "${HOME}/.config/gcloud/application_default_credentials.json" ]]; then
  echo -e "\n\033[1;34m▶︎ Authenticating gcloud with service account\033[0m"
  printf '%s\n' "${GCP_SA_JSON}" >/tmp/sa.json
  gcloud auth activate-service-account --key-file=/tmp/sa.json --quiet
  gcloud config set project "$(jq -r '.project_id' /tmp/sa.json)"
  rm /tmp/sa.json
fi

###############################################################################
# 2. Supabase CLI (requires Node which the feature provided)
###############################################################################
if ! command -v supabase &>/dev/null; then
  echo -e "\n\033[1;34m▶︎ Installing Supabase CLI\033[0m"
  npm install -g --silent supabase
fi

###############################################################################
# 3. Poetry & project dependencies
###############################################################################
if ! command -v poetry &>/dev/null; then
  echo -e "\n\033[1;34m▶︎ Installing Poetry\033[0m"
  pip install --no-cache-dir --quiet poetry
fi

# Local virtual‑env inside workspace for VS Code interpreter pick‑up
if [ ! -d .venv ]; then
  echo -e "\n\033[1;34m▶︎ Creating project virtual‑env & installing deps\033[0m"
  poetry config virtualenvs.in-project true
  poetry install --with dev --no-root -q
fi

###############################################################################
# 4. Git hooks (installed only once)
###############################################################################
if [ ! -f .git/hooks/pre-commit ]; then
  echo -e "\n\033[1;34m▶︎ Installing pre‑commit hooks\033[0m"
  poetry run pre-commit install -q
fi

###############################################################################
# 5. Ensure PATHs survive new terminals
###############################################################################
grep -qxF 'export PATH="$HOME/.npm-global/bin:$PATH"' ~/.bashrc ||
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc

echo -e "\n\033[1;32m✅ Environment ready!\033[0m"
