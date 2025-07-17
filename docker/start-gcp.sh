#!/bin/bash
# 🚀 Script de démarrage GCP pour JARVYS Orchestrateur
# ==================================================

set -e

echo "🚀 Démarrage JARVYS Orchestrateur sur GCP Cloud Run"

# Configuration du logging GCP
export GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-"appia-dev"}
export ENVIRONMENT="production"

# Vérifier les variables d'environnement critiques
required_vars=(
    "XAI_API_KEY"
    "GITHUB_TOKEN"
    "SUPABASE_URL"
    "SUPABASE_KEY"
    "OPENAI_API_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variable d'environnement manquante: $var"
        exit 1
    fi
done

echo "✅ Variables d'environnement validées"

# Cloner les repositories nécessaires
echo "📁 Clonage des repositories..."

# Créer les répertoires
mkdir -p /app/appia-dev /app/appIA

# Cloner appia-dev (branch grok-evolution)
cd /app
if [ ! -d "appia-dev/.git" ]; then
    git clone https://${GITHUB_TOKEN}@github.com/yannabadie/appia-dev.git
fi
cd appia-dev
git checkout grok-evolution
git pull origin grok-evolution

# Cloner appIA (branch main)
cd /app
if [ ! -d "appIA/.git" ]; then
    git clone https://${GITHUB_TOKEN}@github.com/yannabadie/appIA.git
fi
cd appIA
git checkout main
git pull origin main

echo "✅ Repositories synchronisés"

# Démarrer l'interface de commande en arrière-plan
echo "🎛️ Démarrage interface de commande..."
cd /app
python jarvys_command_interface.py &
INTERFACE_PID=$!

echo "✅ Interface de commande démarrée (PID: $INTERFACE_PID)"

# Attendre que l'interface soit prête
sleep 5

# Démarrer l'orchestrateur principal
echo "🤖 Démarrage orchestrateur GROK..."
python grok_orchestrator.py &
ORCHESTRATOR_PID=$!

echo "✅ Orchestrateur démarré (PID: $ORCHESTRATOR_PID)"

# Fonction de nettoyage
cleanup() {
    echo "🔄 Arrêt gracieux des processus..."
    kill $INTERFACE_PID 2>/dev/null || true
    kill $ORCHESTRATOR_PID 2>/dev/null || true
    exit 0
}

# Capturer les signaux d'arrêt
trap cleanup SIGTERM SIGINT

# Monitoring des processus
echo "👁️ Monitoring des processus actif..."
while true; do
    # Vérifier que les processus sont toujours actifs
    if ! kill -0 $INTERFACE_PID 2>/dev/null; then
        echo "❌ Interface de commande arrêtée, redémarrage..."
        python jarvys_command_interface.py &
        INTERFACE_PID=$!
    fi
    
    if ! kill -0 $ORCHESTRATOR_PID 2>/dev/null; then
        echo "❌ Orchestrateur arrêté, redémarrage..."
        python grok_orchestrator.py &
        ORCHESTRATOR_PID=$!
    fi
    
    # Status check toutes les 60 secondes
    sleep 60
    echo "💓 Processus actifs - Interface: $INTERFACE_PID, Orchestrateur: $ORCHESTRATOR_PID"
done
