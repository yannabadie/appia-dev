#!/usr/bin/env bash

echo "=== Application des corrections du script setup.sh ==="

# Vérifier si on est dans le bon répertoire
if [[ ! -f ".devcontainer/setup.sh" ]]; then
    echo "❌ Script à exécuter depuis la racine du projet (/workspaces/appia-dev)"
    exit 1
fi

# Sauvegarder l'original
echo "📁 Sauvegarde de l'original..."
cp .devcontainer/setup.sh .devcontainer/setup.sh.backup
echo "✅ Sauvegarde créée: .devcontainer/setup.sh.backup"

# Appliquer les corrections
echo "🔧 Application des corrections..."
cp .devcontainer/setup_optimized.sh .devcontainer/setup.sh
echo "✅ Corrections appliquées"

# Rendre exécutable
chmod +x .devcontainer/setup.sh
echo "✅ Permissions définies"

echo ""
echo "🎉 Corrections appliquées avec succès !"
echo ""
echo "Le script setup.sh a été corrigé avec :"
echo "  - Détection améliorée de npm/Node.js"
echo "  - URL Supabase CLI corrigée (v2.30.4)"
echo "  - Gestion d'erreurs robuste"
echo "  - Logs améliorés"
echo ""
echo "Pour tester le nouveau script :"
echo "  bash .devcontainer/setup.sh"
echo ""
echo "Pour annuler les modifications :"
echo "  cp .devcontainer/setup.sh.backup .devcontainer/setup.sh"
