#!/bin/bash
# 🚀 DÉPLOIEMENT ORCHESTRATEUR JARVYS AUTONOME GCP
# ===============================================

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-doublenumerique-yann}"
REGION="europe-west1"
SERVICE_NAME="jarvys-orchestrator"

echo "🤖 Déploiement JARVYS Orchestrator Autonome sur GCP"
echo "📋 Projet: $PROJECT_ID"
echo "🌍 Région: $REGION"
echo "🚀 Service: $SERVICE_NAME"
echo ""

# Vérifications préalables
echo "🔍 Vérification des prérequis..."
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI non trouvé"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trouvé"
    exit 1
fi

echo "🔧 Configuration du projet..."
gcloud config set project $PROJECT_ID

echo "🔌 Activation des APIs GCP..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

echo "🔐 Configuration des secrets..."

# Créer les secrets si nécessaire
create_secret_if_not_exists() {
    local secret_name=$1
    local secret_value=$2
    
    if ! gcloud secrets describe $secret_name &>/dev/null; then
        echo "📝 Création du secret $secret_name..."
        echo "$secret_value" | gcloud secrets create $secret_name --data-file=-
    else
        echo "✅ Secret $secret_name existe déjà"
    fi
}

# Secrets configuration
if [ ! -z "$SUPABASE_KEY" ]; then
    create_secret_if_not_exists "supabase-key" "$SUPABASE_KEY"
fi

if [ ! -z "$GITHUB_TOKEN" ]; then
    create_secret_if_not_exists "github-token" "$GITHUB_TOKEN"
fi

if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    create_secret_if_not_exists "anthropic-api-key" "$ANTHROPIC_API_KEY"
fi

echo "🏗️ Lancement du build et déploiement..."
gcloud builds submit . \
    --config=cloudbuild.yaml \
    --project=$PROJECT_ID \
    --substitutions=_REGION=$REGION

# Récupérer l'URL du service
echo "🔍 Récupération de l'URL du service..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)")

if [ $? -eq 0 ] && [ ! -z "$SERVICE_URL" ]; then
    echo ""
    echo "🎉 DÉPLOIEMENT ORCHESTRATEUR RÉUSSI!"
    echo ""
    echo "📊 INFORMATIONS DÉPLOIEMENT:"
    echo "   🌐 URL: $SERVICE_URL"
    echo "   📍 Région: $REGION"
    echo "   🚀 Service: $SERVICE_NAME"
    echo "   📋 Projet: $PROJECT_ID"
    echo ""
    echo "🔗 ENDPOINTS DISPONIBLES:"
    echo "   📊 Status: $SERVICE_URL/status"
    echo "   💬 Chat: $SERVICE_URL/chat"
    echo "   🔍 Health: $SERVICE_URL/health"
    echo "   🌐 WebSocket: $SERVICE_URL/ws"
    echo ""
    echo "🎯 PROCHAINES ÉTAPES:"
    echo "   1. Tester: curl $SERVICE_URL/health"
    echo "   2. Vérifier: curl $SERVICE_URL/status"
    echo "   3. Configurer dashboard pour pointer vers: $SERVICE_URL"
    echo ""
    echo "✅ JARVYS fonctionne maintenant 24/7 de manière autonome!"
    echo "🤖 Votre assistant IA est indépendant de Codespace!"
else
    echo "❌ Erreur lors de la récupération de l'URL du service"
    exit 1
fi
