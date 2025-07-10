#!/usr/bin/env bash

echo "=== Test des corrections du script setup.sh ==="

# Test 1: Vérifier que Node.js et npm sont trouvés
echo "1. Vérification de Node.js et npm..."
if command -v node &>/dev/null; then
    echo "✅ Node.js trouvé: $(node --version)"
else
    echo "❌ Node.js non trouvé"
fi

if command -v npm &>/dev/null; then
    echo "✅ npm trouvé: $(npm --version)"
else
    echo "❌ npm non trouvé"
fi

# Test 2: Vérifier que les chemins nvm sont configurés
echo -e "\n2. Vérification des chemins NVM..."
NVM_DIR=/usr/local/share/nvm
if [[ -d "$NVM_DIR" ]]; then
    echo "✅ Répertoire NVM trouvé: $NVM_DIR"
    echo "   Contenu: $(ls -la $NVM_DIR 2>/dev/null || echo 'vide')"
else
    echo "❌ Répertoire NVM non trouvé"
fi

# Test 3: Vérifier la version Supabase
echo -e "\n3. Test de l'URL Supabase..."
SUPABASE_VERSION="1.201.2"
URL="https://github.com/supabase/cli/releases/download/v${SUPABASE_VERSION}/supabase_${SUPABASE_VERSION}_linux_amd64.tar.gz"
if curl -fsSL --head "$URL" > /dev/null 2>&1; then
    echo "✅ URL Supabase valide: $URL"
else
    echo "❌ URL Supabase invalide: $URL"
    echo "   Tentative de vérifier les versions disponibles..."
    curl -s https://api.github.com/repos/supabase/cli/releases/latest | grep '"tag_name"' | head -1 | cut -d'"' -f4 || echo "Impossible de récupérer la version"
fi

# Test 4: Vérifier le PATH actuel
echo -e "\n4. Analyse du PATH actuel..."
echo "PATH: $PATH"
echo "Emplacements npm potentiels:"
for npm_path in /usr/local/bin/npm /usr/bin/npm ~/.local/bin/npm "${NVM_DIR}/versions/node/*/bin/npm"; do
    if [[ -x "$npm_path" ]]; then
        echo "  ✅ $npm_path"
    else
        echo "  ❌ $npm_path (non trouvé)"
    fi
done

echo -e "\n=== Fin des tests ==="
