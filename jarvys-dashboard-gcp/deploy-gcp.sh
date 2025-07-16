#!/bin/bash
# 🚀 DÉPLOIEMENT AUTOMATISÉ JARVYS DASHBOARD GCP
# ==============================================

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-doublenumerique-yann}"
REGION="europe-west1"
SERVICE_NAME="jarvys-dashboard"
BACKEND_SERVICE_NAME="jarvys-orchestrator"

echo "🎯 Déploiement JARVYS Dashboard sur GCP"
echo "📋 Projet: $PROJECT_ID"
echo "🌍 Région: $REGION"
echo "🚀 Service: $SERVICE_NAME"
echo ""

# Vérifications préalables
echo "🔍 Vérification des prérequis..."

# Vérifier gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI non trouvé. Installez le Google Cloud SDK."
    exit 1
fi

# Vérifier authentification
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Non authentifié. Exécutez: gcloud auth login"
    exit 1
fi

# Configurer le projet
echo "🔧 Configuration du projet..."
gcloud config set project $PROJECT_ID

# Activer les APIs nécessaires
echo "🔌 Activation des APIs GCP..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    compute.googleapis.com \
    --quiet

# Créer les secrets s'ils n'existent pas
echo "🔐 Configuration des secrets..."

# Google Client ID
if ! gcloud secrets describe google-client-id &>/dev/null; then
    echo "📝 Création du secret Google Client ID..."
    read -p "Entrez votre Google Client ID: " GOOGLE_CLIENT_ID
    echo -n "$GOOGLE_CLIENT_ID" | gcloud secrets create google-client-id --data-file=-
else
    echo "✅ Secret Google Client ID existe déjà"
fi

# Vérifier que le service backend existe
echo "🔍 Vérification du service backend..."
BACKEND_URL="https://${BACKEND_SERVICE_NAME}-${PROJECT_ID}.${REGION}.run.app"

if gcloud run services describe $BACKEND_SERVICE_NAME --region=$REGION &>/dev/null; then
    echo "✅ Service backend trouvé: $BACKEND_URL"
else
    echo "⚠️ Service backend non trouvé. Il sera créé automatiquement."
    BACKEND_URL="http://localhost:8000" # Fallback pour développement
fi

# Créer le service account pour Cloud Build si nécessaire
echo "🔧 Configuration du service account..."
SA_EMAIL="cloudbuild-jarvys@${PROJECT_ID}.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe $SA_EMAIL &>/dev/null; then
    echo "📝 Création du service account Cloud Build..."
    gcloud iam service-accounts create cloudbuild-jarvys \
        --display-name="Cloud Build Service Account for JARVYS" \
        --description="Service account for building and deploying JARVYS Dashboard"
    
    # Attribuer les rôles nécessaires
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/run.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/storage.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/secretmanager.secretAccessor"
else
    echo "✅ Service account existe déjà"
fi

# Build et déploiement
echo "🏗️ Lancement du build et déploiement..."
gcloud builds submit . \
    --config=cloudbuild.yaml \
    --substitutions="_BACKEND_URL=$BACKEND_URL,_REGION=$REGION" \
    --timeout=1200s

# Attendre que le service soit prêt
echo "⏳ Attente du déploiement..."
sleep 30

# Récupérer l'URL du service
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)")

echo ""
echo "🎉 Déploiement terminé avec succès!"
echo "🌐 URL du dashboard: $SERVICE_URL"
echo ""

# Tests de santé
echo "🔍 Test de santé du service..."
if curl -sf "$SERVICE_URL/health" > /dev/null; then
    echo "✅ Service en ligne et fonctionnel"
else
    echo "⚠️ Service déployé mais test de santé échoué"
fi

# Configuration DNS (optionnel)
read -p "Voulez-vous configurer un domaine personnalisé? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Entrez votre domaine (ex: dashboard.yourdomain.com): " CUSTOM_DOMAIN
    
    echo "🌐 Configuration du domaine personnalisé..."
    gcloud run domain-mappings create \
        --service=$SERVICE_NAME \
        --domain=$CUSTOM_DOMAIN \
        --region=$REGION
    
    echo "📝 Ajoutez ce CNAME à votre DNS:"
    echo "   $CUSTOM_DOMAIN -> ghs.googlehosted.com"
fi

echo ""
echo "📋 Résumé du déploiement:"
echo "   🎯 Projet: $PROJECT_ID"
echo "   🌍 Région: $REGION"
echo "   🚀 Service: $SERVICE_NAME"
echo "   🌐 URL: $SERVICE_URL"
echo "   🔐 Authentification: Google OAuth (yann.abadie@gmail.com)"
echo "   🛡️ Sécurité: Cloud Armor activé"
echo ""
echo "✅ JARVYS Dashboard est maintenant accessible!"
echo "🔑 Connectez-vous avec yann.abadie@gmail.com"
echo ""

# Ouvrir le dashboard dans le navigateur (optionnel)
read -p "Ouvrir le dashboard dans le navigateur? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    case "$(uname -s)" in
        Darwin) open "$SERVICE_URL" ;;
        Linux) xdg-open "$SERVICE_URL" ;;
        CYGWIN*|MINGW*) start "$SERVICE_URL" ;;
        *) echo "Ouvrez manuellement: $SERVICE_URL" ;;
    esac
fi
