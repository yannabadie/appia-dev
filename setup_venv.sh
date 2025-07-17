#!/bin/bash
# 🔧 Script de setup environnement virtuel optimisé pour Grok Orchestrator

echo "🚀 Setup environnement virtuel pour Grok Orchestrator..."

# Nettoyage des anciens venv si problématiques
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "⚠️ Désactivation environnement virtuel existant..."
    deactivate || true
fi

# Suppression ancien venv corrompu si existant
if [[ -d ".venv" ]]; then
    echo "🧹 Nettoyage ancien environnement..."
    rm -rf .venv
fi

# Création nouvel environnement propre
echo "🆕 Création nouvel environnement virtuel..."
python3 -m venv .venv

# Activation
echo "⚡ Activation environnement..."
source .venv/bin/activate

# Vérification activation
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Erreur: Environnement virtuel non activé"
    exit 1
fi

echo "✅ Environnement virtuel activé: $VIRTUAL_ENV"

# Mise à jour pip
echo "📦 Mise à jour pip..."
pip install --upgrade pip

# Installation des dépendances optimisées
echo "🔽 Installation dépendances Grok Orchestrator..."
pip install -r requirements-grok.txt

# Vérification installation
echo "🧪 Vérification installation..."
python -c "import langgraph; print('✅ LangGraph:', langgraph.__version__)"
python -c "import github; print('✅ PyGithub:', github.__version__)"
python -c "import supabase; print('✅ Supabase: OK')"
python -c "import urllib3; print('✅ urllib3:', urllib3.__version__)"

echo "🎉 Setup terminé avec succès!"
echo "💡 Pour activer: source .venv/bin/activate"
echo "🚀 Pour lancer: python grok_orchestrator.py"
