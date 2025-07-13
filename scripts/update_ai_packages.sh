#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Script de mise à jour des packages AI vers les dernières versions
# Usage: ./update_ai_packages.sh
################################################################################

log_info() { echo "ℹ️  $1"; }
log_success() { echo "✅ $1"; }
log_error() { echo "❌ $1"; }

echo "🤖 Mise à jour des packages AI vers les dernières versions"
echo "=================================================="

# Packages AI principaux à maintenir à jour
AI_PACKAGES=(
    "anthropic"
    "google-generativeai" 
    "openai"
)

# Vérifier les versions actuelles
echo ""
log_info "Versions actuelles :"
for package in "${AI_PACKAGES[@]}"; do
    case $package in
        "google-generativeai")
            if python -c "import google.generativeai as genai; print(f'  - google-generativeai: {genai.__version__}')" 2>/dev/null; then
                :
            else
                echo "  - $package: ❌ non installé"
            fi
            ;;
        *)
            if python -c "import $package; print(f'  - $package: {$package.__version__}')" 2>/dev/null; then
                :
            else
                echo "  - $package: ❌ non installé"
            fi
            ;;
    esac
done

echo ""
log_info "Mise à jour vers les dernières versions..."

# Mettre à jour avec pip (plus rapide que poetry pour les mises à jour)
if pip install --upgrade "${AI_PACKAGES[@]}"; then
    log_success "Packages AI mis à jour avec succès"
else
    log_error "Échec de la mise à jour des packages AI"
    exit 1
fi

# Vérifier les nouvelles versions
echo ""
log_info "Nouvelles versions :"
for package in "${AI_PACKAGES[@]}"; do
    if python -c "import $package; print(f'  - $package: {$package.__version__}')" 2>/dev/null; then
        :
    else
        echo "  - $package: ❌ problème d'import"
    fi
done

echo ""
log_success "Mise à jour terminée !"

# Optionnel: Mettre à jour pyproject.toml et requirements.txt avec les nouvelles versions
if command -v poetry &> /dev/null; then
    echo ""
    log_info "Mise à jour du fichier poetry.lock..."
    if poetry lock; then
        log_success "Fichier poetry.lock mis à jour"
    else
        log_error "Échec mise à jour poetry.lock (non critique)"
    fi
fi

echo ""
echo "💡 Conseil: Pensez à tester vos intégrations AI après cette mise à jour"
