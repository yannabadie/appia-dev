#!/usr/bin/env bash
set -euo pipefail

# --- paramètres -------------------------------------------------------------
# 1) si l’ID est passé en argument, on l’utilise
PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"

if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "(unset)" ]]; then
  echo "❌  No GCP project ID. Pass it as argument or run 'gcloud config set project <ID>'."
  exit 1
fi

REGION="europe-west1"
IMAGE="gcr.io/${PROJECT_ID}/jarvys-mcp"

# --- build & déploiement ----------------------------------------------------
echo "🔧  Building and deploying to project: $PROJECT_ID"

gcloud builds submit --tag "$IMAGE"

gcloud run deploy jarvys-mcp \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated
