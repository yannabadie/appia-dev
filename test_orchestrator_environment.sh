#!/bin/bash

echo "🧪 SCRIPT DE TEST ORCHESTRATEUR GROK-CLAUDE 4"
echo "============================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Vérification de l'environnement
print_status "Vérification de l'environnement Python..."
python3 --version
if [ $? -eq 0 ]; then
    print_success "Python 3 disponible"
else
    print_error "Python 3 non trouvé"
    exit 1
fi

# 2. Vérification de la syntaxe
print_status "Vérification de la syntaxe de grok_orchestrator.py..."
python3 -m py_compile grok_orchestrator.py
if [ $? -eq 0 ]; then
    print_success "Syntaxe validée"
else
    print_error "Erreurs de syntaxe détectées"
    exit 1
fi

# 3. Affichage des variables d'environnement (sans révéler les clés)
print_status "Variables d'environnement disponibles:"
echo "  - XAI_API_KEY: $([ ! -z "$XAI_API_KEY" ] && echo "✅ Définie" || echo "❌ Manquante")"
echo "  - CLAUDE_API_KEY: $([ ! -z "$CLAUDE_API_KEY" ] && echo "✅ Définie" || echo "❌ Manquante")"
echo "  - SUPABASE_URL: $([ ! -z "$SUPABASE_URL" ] && echo "✅ Définie" || echo "❌ Manquante")"
echo "  - SUPABASE_KEY: $([ ! -z "$SUPABASE_KEY" ] && echo "✅ Définie" || echo "❌ Manquante")"
echo "  - GITHUB_TOKEN: $([ ! -z "$GITHUB_TOKEN" ] && echo "✅ Définie" || echo "❌ Manquante")"

# 4. Création du schéma Supabase si nécessaire
if [ ! -z "$SUPABASE_URL" ] && [ ! -z "$SUPABASE_KEY" ]; then
    print_status "Schéma Supabase disponible dans create_orchestrator_schema.sql"
    print_warning "Exécutez le schéma dans votre console Supabase si les tables n'existent pas"
else
    print_warning "Configuration Supabase manquante - l'orchestrateur fonctionnera en mode local"
fi

# 5. Test de base (import des modules)
print_status "Test d'import des modules Python..."
python3 -c "
try:
    import requests
    import json
    import os
    from typing import Dict, Any, List
    print('✅ Modules de base importés avec succès')
except ImportError as e:
    print(f'❌ Erreur d\\'import: {e}')
    exit(1)
"

# 6. Test du LangGraph
print_status "Test de LangGraph..."
python3 -c "
try:
    from langgraph.graph import END, StateGraph
    from typing_extensions import Annotated, TypedDict
    print('✅ LangGraph importé avec succès')
except ImportError as e:
    print(f'⚠️ LangGraph non disponible: {e}')
    print('Installation: pip install langgraph')
"

# 7. Test des SDKs optionnels
print_status "Test des SDKs optionnels..."
python3 -c "
# Test xAI SDK
try:
    from xai_sdk import Client
    print('✅ xAI SDK disponible')
except ImportError:
    print('⚠️ xAI SDK non disponible (utilisation fallback REST)')

# Test Anthropic SDK
try:
    import anthropic
    print('✅ Anthropic SDK disponible')
except ImportError:
    print('⚠️ Anthropic SDK non disponible (validation code désactivée)')

# Test Supabase
try:
    from supabase import create_client
    print('✅ Supabase client disponible')
except ImportError:
    print('⚠️ Supabase client non disponible (mémoire locale)')

# Test GitHub
try:
    from github import Github
    print('✅ PyGithub disponible')
except ImportError:
    print('⚠️ PyGithub non disponible (intégration GitHub limitée)')
"

echo ""
print_status "=========================================="
print_status "RÉSUMÉ DE L'ENVIRONNEMENT"
print_status "=========================================="

# Mode de fonctionnement déterminé
if [ ! -z "$XAI_API_KEY" ] && [ ! -z "$CLAUDE_API_KEY" ] && [ ! -z "$SUPABASE_URL" ]; then
    print_success "🚀 MODE COMPLET: Toutes les APIs disponibles"
elif [ ! -z "$XAI_API_KEY" ]; then
    print_warning "⚡ MODE GROK: API Grok disponible, fonctionnalités limitées"
else
    print_warning "🔧 MODE TEST: APIs simulées, parfait pour développement"
fi

echo ""
print_status "Commandes de lancement disponibles:"
echo "  1. Test basique:           python3 grok_orchestrator.py"
echo "  2. Mode observation:       JARVYS_OBSERVATION_MODE=true python3 grok_orchestrator.py"
echo "  3. Un seul cycle:          JARVYS_SINGLE_CYCLE=true python3 grok_orchestrator.py"

echo ""
print_success "🎯 Environnement de test prêt !"
print_status "Lancez l'orchestrateur quand vous le souhaitez."
