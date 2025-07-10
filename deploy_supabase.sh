#!/bin/bash

# Script de déploiement local JARVYS Dashboard sur Supabase
# Usage: ./deploy_supabase.sh [test|deploy]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FUNCTIONS_DIR="$PROJECT_ROOT/supabase/functions"

echo -e "${BLUE}🚀 JARVYS Dashboard - Déploiement Supabase${NC}"
echo "=================================="

# Vérifier les prérequis
check_prerequisites() {
    echo -e "${YELLOW}🔍 Vérification des prérequis...${NC}"
    
    # Vérifier Deno
    if ! command -v deno &> /dev/null; then
        echo -e "${RED}❌ Deno n'est pas installé${NC}"
        echo "Installation: curl -fsSL https://deno.land/install.sh | sh"
        exit 1
    fi
    
    # Vérifier Supabase CLI
    if ! command -v supabase &> /dev/null; then
        echo -e "${RED}❌ Supabase CLI n'est pas installé${NC}"
        echo "Installation: npm install -g supabase"
        exit 1
    fi
    
    # Vérifier les variables d'environnement
    if [ -z "$SUPABASE_ACCESS_TOKEN" ] && [ "$1" != "test" ]; then
        echo -e "${RED}❌ SUPABASE_ACCESS_TOKEN non défini${NC}"
        echo "Exportez votre token: export SUPABASE_ACCESS_TOKEN=your_token"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prérequis vérifiés${NC}"
}

# Fonction pour tester localement
test_local() {
    echo -e "${YELLOW}🧪 Test local des Edge Functions...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # Démarrer Supabase localement
    echo "Démarrage de Supabase local..."
    supabase start
    
    # Déployer les fonctions localement
    echo "Déploiement local des fonctions..."
    supabase functions serve jarvys-dashboard &
    SERVE_PID=$!
    
    # Attendre que le serveur démarre
    sleep 5
    
    # Tester les endpoints
    echo "Test des endpoints..."
    
    # Test status
    echo "- Test /api/status..."
    curl -s "http://localhost:54321/functions/v1/jarvys-dashboard/api/status" | jq .
    
    # Test metrics
    echo "- Test /api/metrics..."
    curl -s "http://localhost:54321/functions/v1/jarvys-dashboard/api/metrics" | jq .
    
    # Nettoyer
    kill $SERVE_PID 2>/dev/null || true
    supabase stop
    
    echo -e "${GREEN}✅ Tests locaux terminés${NC}"
}

# Fonction pour déployer en production
deploy_production() {
    echo -e "${YELLOW}🚀 Déploiement en production...${NC}"
    
    if [ -z "$SUPABASE_PROJECT_ID" ]; then
        echo -e "${RED}❌ SUPABASE_PROJECT_ID non défini${NC}"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # Lier le projet
    echo "Liaison avec le projet Supabase..."
    supabase link --project-ref "$SUPABASE_PROJECT_ID"
    
    # Déployer les fonctions
    echo "Déploiement des Edge Functions..."
    supabase functions deploy jarvys-dashboard
    
    # Tester le déploiement
    echo "Test du déploiement..."
    FUNCTION_URL="https://$SUPABASE_PROJECT_ID.functions.supabase.co/jarvys-dashboard"
    
    sleep 5
    
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FUNCTION_URL/api/status")
    
    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}✅ Déploiement réussi!${NC}"
        echo -e "${BLUE}🌐 Dashboard URL: $FUNCTION_URL${NC}"
        echo -e "${BLUE}📊 API Status: $FUNCTION_URL/api/status${NC}"
    else
        echo -e "${RED}❌ Erreur de déploiement (Code: $RESPONSE)${NC}"
        exit 1
    fi
}

# Fonction d'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  test     - Tester localement avec Supabase local"
    echo "  deploy   - Déployer en production sur Supabase"
    echo "  help     - Afficher cette aide"
    echo ""
    echo "Variables d'environnement requises pour le déploiement:"
    echo "  SUPABASE_ACCESS_TOKEN - Token d'accès Supabase"
    echo "  SUPABASE_PROJECT_ID   - ID du projet Supabase"
}

# Main
case "${1:-}" in
    "test")
        check_prerequisites test
        test_local
        ;;
    "deploy")
        check_prerequisites deploy
        deploy_production
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Commande inconnue: ${1:-}${NC}"
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Terminé!${NC}"
