#!/usr/bin/env bash
set -euo pipefail

################################################################################
# 0. Variables & fonctions utilitaires
################################################################################
export DEBIAN_FRONTEND=noninteractive
export CLOUDSDK_CORE_DISABLE_PROMPTS=1   # Plus aucun prompt gcloud
NVM_DIR=/usr/local/share/nvm             # Chemin utilisé par la feature Node
SUPABASE_VERSION=${SUPABASE_VERSION:-2.30.4}   # Dernière version stable

silent_apt_update() { sudo apt-get update -qq; }
apt_install()      { silent_apt_update && sudo apt-get install -yqq "$@"; }

have_cmd() { command -v "$1" &>/dev/null; }

log_section() { echo -e "\n▶︎ $1"; }
log_success() { echo "✅ $1"; }
log_error() { echo "❌ $1"; }
log_info() { echo "ℹ️  $1"; }

################################################################################
# 1. Dépendances système de base
################################################################################
log_section "Installation des dépendances APT de base"
apt_install curl gnupg ca-certificates apt-transport-https jq tar gzip

################################################################################
# 2. Google Cloud CLI
################################################################################
if ! have_cmd gcloud; then
  log_section "Installation Google Cloud CLI"
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
https://packages.cloud.google.com/apt cloud-sdk main" \
      | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
      | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  apt_install google-cloud-cli
  log_success "Google Cloud CLI installé"
else
  log_success "Google Cloud CLI déjà présent"
fi

if [[ -n "${GCP_SA_JSON:-}" ]]; then
  log_section "Authentification GCP (service account)"
  SA_FILE=$(mktemp)
  echo "${GCP_SA_JSON}" > "${SA_FILE}"
  gcloud auth activate-service-account --key-file="${SA_FILE}" --quiet
  PROJECT_ID=$(jq -r '.project_id' "${SA_FILE}")
  gcloud config set project "${PROJECT_ID}" --quiet || true
  rm -f "${SA_FILE}"
  log_success "Authentification GCP configurée"

  log_section "Activation des APIs (Cloud Resource Manager + requises)"
  gcloud services enable \
    cloudresourcemanager.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    iamcredentials.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    --quiet || true
  log_success "APIs GCP activées"
fi

################################################################################
# 3. Configuration de l'environnement Node.js/npm
################################################################################
log_section "Configuration de l'environnement Node.js"

# Charger nvm si disponible
if [[ -s "${NVM_DIR}/nvm.sh" ]]; then
  source "${NVM_DIR}/nvm.sh"
  nvm use default &>/dev/null || nvm use node &>/dev/null || true
elif [[ -d "${NVM_DIR}" ]]; then
  # Ajout des binaires Node au PATH
  for vdir in "${NVM_DIR}/versions/node"/*/bin; do
    [[ -d "$vdir" ]] && PATH="$vdir:$PATH"
  done
  export PATH
fi

# Diagnostic
log_info "État des outils de développement :"
log_info "  - Node.js: $(node --version 2>/dev/null || echo 'non trouvé')"
log_info "  - npm: $(npm --version 2>/dev/null || echo 'non trouvé')"

if have_cmd node && have_cmd npm; then
  log_success "Environnement Node.js/npm configuré"
else
  log_error "Problème avec l'environnement Node.js/npm"
fi

################################################################################
# 4. Installation Supabase CLI
################################################################################
install_supabase() {
  log_section "Installation Supabase CLI (binary ${SUPABASE_VERSION})"
  URL="https://github.com/supabase/cli/releases/download/v${SUPABASE_VERSION}/supabase_linux_amd64.tar.gz"
  TMP_DIR=$(mktemp -d)
  
  if curl -fsSL "$URL" | tar -xz -C "$TMP_DIR" 2>/dev/null; then
    sudo install -m 0755 "$TMP_DIR/supabase" /usr/local/bin/supabase
    rm -rf "$TMP_DIR"
    log_success "Supabase CLI ${SUPABASE_VERSION} installé avec succès"
  else
    log_error "Échec installation binary, tentative via script officiel"
    rm -rf "$TMP_DIR"
    curl -fsSL https://raw.githubusercontent.com/supabase/cli/main/scripts/install.sh | bash
  fi
}

if have_cmd supabase; then
  log_success "Supabase CLI déjà présent : $(supabase --version)"
elif have_cmd npm; then
  log_section "Installation Supabase CLI via npm"
  if sudo npm install -g --silent supabase 2>/dev/null; then
    log_success "Supabase CLI installé via npm"
  else
    log_error "Échec installation npm, fallback vers binary"
    install_supabase
  fi
else
  install_supabase
fi

################################################################################
# 5. Poetry + dépendances Python
################################################################################
# Vérification de la version Python
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log_info "Version Python détectée: $PYTHON_VERSION"

if ! have_cmd poetry; then
  log_section "Installation Poetry"
  python -m pip install --no-cache-dir --quiet poetry
  log_success "Poetry installé"
else
  log_success "Poetry déjà présent"
fi

# Configuration Poetry pour éviter les conflits de versions
log_section "Configuration Poetry"
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
log_success "Configuration Poetry appliquée"

log_section "Installation dépendances Python (poetry install --with dev)"
# Vérifier et régénérer le lock file si nécessaire
if ! poetry check --lock 2>/dev/null; then
  log_info "Fichier poetry.lock désynchronisé, régénération..."
  if poetry lock; then
    log_success "Fichier poetry.lock régénéré"
  else
    log_error "Échec régénération poetry.lock"
  fi
fi

if poetry install --with dev --no-root --no-interaction; then
  log_success "Dépendances Python installées"
  
  # Mise à jour automatique des packages AI vers les dernières versions
  log_section "Mise à jour des packages AI vers les dernières versions"
  if poetry run pip install --upgrade anthropic google-generativeai openai; then
    log_success "Packages AI mis à jour vers les dernières versions"
  else
    log_info "Échec mise à jour packages AI (non critique)"
  fi
else
  log_error "Échec installation dépendances Python"
fi

################################################################################
# 6. Hooks git pré-commit
################################################################################
log_section "Installation hooks pre-commit"
if poetry run pre-commit install --install-hooks --overwrite; then
  log_success "Hooks pre-commit installés"
else
  log_error "Échec installation hooks pre-commit"
fi

################################################################################
# 7. Résumé final
################################################################################
log_section "Vérification finale de l'environnement"
log_info "Outils installés :"
log_info "  - Node.js: $(node --version 2>/dev/null || echo '❌ non trouvé')"
log_info "  - npm: $(npm --version 2>/dev/null || echo '❌ non trouvé')"
log_info "  - gcloud: $(gcloud --version 2>/dev/null | head -1 || echo '❌ non trouvé')"
log_info "  - poetry: $(poetry --version 2>/dev/null || echo '❌ non trouvé')"
log_info "  - supabase: $(supabase --version 2>/dev/null || echo '❌ non trouvé')"

log_section "Versions des packages AI"
if poetry run python -c "
import anthropic, google.generativeai, openai
print(f'  - anthropic: {anthropic.__version__}')
print(f'  - google-generativeai: {google.generativeai.__version__}')  
print(f'  - openai: {openai.__version__}')
" 2>/dev/null; then
  log_success "Packages AI installés et fonctionnels"
else
  log_error "Problème avec les packages AI"
fi

echo -e "\n✅ Environnement prêt !"
