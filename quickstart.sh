#!/bin/bash
# 🚀 JARVYS Quick Start Script

echo "🤖 JARVYS System Quick Start"
echo "=============================="

# Vérifier les prérequis
echo "🔍 Vérification des prérequis..."

if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry non trouvé. Installation..."
    pip install poetry
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 requis"
    exit 1
fi

echo "✅ Prérequis OK"

# Installer les dépendances
echo "📦 Installation des dépendances..."
poetry install --with dev

# Valider l'installation
echo "🔍 Validation de l'installation..."
poetry run python -c "import jarvys_dev; print('✅ JARVYS_DEV module OK')"

# Générer la documentation
echo "📚 Génération de la documentation..."
poetry run python scripts/generate_wiki_docs.py

# Options de démarrage
echo ""
echo "🎯 Options de démarrage :"
echo "  1. JARVYS_DEV Agent : poetry run python src/jarvys_dev/main.py"
echo "  2. Dashboard Local  : cd dashboard_local && python dashboard_local.py"
echo "  3. Tests Workflow   : python test_workflows.py"
echo ""

# Démarrage automatique du dashboard si demandé
if [ "$1" = "--dashboard" ]; then
    echo "🚀 Démarrage du dashboard local..."
    cd dashboard_local
    python dashboard_local.py
fi

echo "✅ JARVYS System prêt !"
