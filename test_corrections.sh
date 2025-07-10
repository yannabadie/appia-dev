#!/usr/bin/env bash

echo "=== Test du script setup.sh corrigé ==="

# Simuler l'environnement du script setup.sh
export DEBIAN_FRONTEND=noninteractive
export CLOUDSDK_CORE_DISABLE_PROMPTS=1
NVM_DIR=/usr/local/share/nvm
SUPABASE_VERSION=${SUPABASE_VERSION:-2.30.4}

have_cmd() { command -v "$1" &>/dev/null; }

echo "1. Test de détection des outils..."
echo "  - Node.js: $(have_cmd node && node --version || echo 'NON TROUVÉ')"
echo "  - npm: $(have_cmd npm && npm --version || echo 'NON TROUVÉ')"
echo "  - gcloud: $(have_cmd gcloud && echo 'TROUVÉ' || echo 'NON TROUVÉ')"
echo "  - poetry: $(have_cmd poetry && echo 'TROUVÉ' || echo 'NON TROUVÉ')"
echo "  - supabase: $(have_cmd supabase && supabase --version || echo 'NON TROUVÉ')"

echo -e "\n2. Test URL Supabase..."
URL="https://github.com/supabase/cli/releases/download/v${SUPABASE_VERSION}/supabase_linux_amd64.tar.gz"
if curl -fsSL --head "$URL" > /dev/null 2>&1; then
    echo "✅ URL Supabase valide: $URL"
else
    echo "❌ URL Supabase invalide: $URL"
fi

echo -e "\n3. Test installation simulée Supabase (sans installation réelle)..."
install_supabase_test() {
  echo "   Téléchargement simulé depuis: $URL"
  TMP_DIR=$(mktemp -d)
  if curl -fsSL "$URL" | tar -tz -C "$TMP_DIR" > /dev/null 2>&1; then
    echo "   ✅ Archive téléchargée et extractible"
    rm -rf "$TMP_DIR"
    return 0
  else
    echo "   ❌ Échec du téléchargement/extraction"
    rm -rf "$TMP_DIR"
    return 1
  fi
}

install_supabase_test

echo -e "\n4. Test des chemins NPM..."
echo "   PATH actuel contient:"
echo "$PATH" | tr ':' '\n' | grep -E "(node|npm|nvm)" | head -5

echo -e "\n=== Résumé ==="
if have_cmd node && have_cmd npm; then
    echo "✅ Environnement Node.js/npm: OK"
else
    echo "❌ Environnement Node.js/npm: PROBLÈME"
fi

if curl -fsSL --head "$URL" > /dev/null 2>&1; then
    echo "✅ URL Supabase: OK"
else
    echo "❌ URL Supabase: PROBLÈME"
fi

echo "=== Fin des tests ==="
