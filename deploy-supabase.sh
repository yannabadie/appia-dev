#!/bin/bash
# Script de déploiement JARVYS Dashboard sur Supabase Edge Functions

set -e

echo "🚀 Déploiement JARVYS Dashboard sur Supabase..."

# Vérification des prérequis
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI n'est pas installé"
    echo "📥 Installation: npm install -g supabase"
    exit 1
fi

# Vérification de la connexion Supabase
if [ -z "$SUPABASE_ACCESS_TOKEN" ]; then
    echo "⚠️  Variable SUPABASE_ACCESS_TOKEN non définie"
    echo "🔑 Connexion manuelle requise: supabase login"
fi

# Configuration du projet
echo "📋 Configuration du projet Supabase..."
if [ ! -f "supabase/config.toml" ]; then
    echo "❌ Fichier config.toml manquant"
    exit 1
fi

# Vérification de l'Edge Function
if [ ! -f "supabase/functions/jarvys-dashboard/index.ts" ]; then
    echo "❌ Edge Function jarvys-dashboard manquante"
    exit 1
fi

echo "✅ Fichiers vérifiés"

# Déploiement de l'Edge Function
echo "🔄 Déploiement de l'Edge Function jarvys-dashboard..."

supabase functions deploy jarvys-dashboard \
    --project-ref ${SUPABASE_PROJECT_ID:-"your-project-id"} \
    --no-verify-jwt

if [ $? -eq 0 ]; then
    echo "✅ Edge Function déployée avec succès!"
    echo ""
    echo "🌐 Dashboard accessible à:"
    echo "   https://${SUPABASE_PROJECT_ID:-your-project-id}.supabase.co/functions/v1/jarvys-dashboard"
    echo ""
    echo "📚 API Endpoints disponibles:"
    echo "   GET  /api/status    - Statut du système"
    echo "   GET  /api/metrics   - Métriques de performance"  
    echo "   GET  /api/data      - Données complètes"
    echo "   POST /api/chat      - Chat avec JARVYS"
    echo "   GET  /health        - Health check"
    echo ""
    echo "🔐 Secret configuré: SPB_EDGE_FUNCTIONS"
else
    echo "❌ Échec du déploiement"
    exit 1
fi

# Configuration des secrets (optionnel)
if [ ! -z "$SPB_EDGE_FUNCTIONS" ]; then
    echo "🔑 Configuration du secret SPB_EDGE_FUNCTIONS..."
    supabase secrets set SPB_EDGE_FUNCTIONS="$SPB_EDGE_FUNCTIONS" \
        --project-ref ${SUPABASE_PROJECT_ID:-"your-project-id"}
    echo "✅ Secret configuré"
fi

echo ""
echo "🎉 Déploiement terminé avec succès!"
echo "📊 JARVYS Dashboard est maintenant disponible sur Supabase Edge Functions"
