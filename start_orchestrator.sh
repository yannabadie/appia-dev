#!/bin/bash
# Script de démarrage de l'orchestrateur Grok amélioré

echo "🚀 Démarrage de l'orchestrateur Grok..."

# Vérifier .env
if [ ! -f .env ]; then
    echo "❌ Fichier .env manquant"
    echo "💡 Copiez .env.template vers .env et configurez vos clés API"
    exit 1
fi

# Charger les variables d'environnement
set -a
source .env
set +a

# Vérifier les variables essentielles
if [ -z "$GROK_API_KEY" ]; then
    echo "❌ GROK_API_KEY manquant dans .env"
    exit 1
fi

if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ CLAUDE_API_KEY manquant dans .env"
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL manquant dans .env"
    exit 1
fi

echo "✅ Configuration validée"
echo "🧠 Lancement de l'orchestrateur..."

# Lancer l'orchestrateur
python grok_orchestrator.py "$@"
