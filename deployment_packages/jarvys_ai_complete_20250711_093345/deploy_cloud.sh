#!/bin/bash
# JARVYS_AI Cloud Deployment Script (Google Cloud Run)

set -e

echo "☁️  Starting JARVYS_AI Cloud Deployment..."

# Check required tools
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK is not installed."
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    exit 1
fi

# Configuration
read -p "Enter your Google Cloud Project ID: " PROJECT_ID
read -p "Enter region (default: us-central1): " REGION
REGION=${REGION:-us-central1}
SERVICE_NAME="jarvys-ai"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and deploy
echo "🏗️  Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars="JARVYS_MODE=production"

echo ""
echo "✅ JARVYS_AI deployed to Cloud Run successfully!"
echo "🌐 Access your deployment at the URL shown above"
