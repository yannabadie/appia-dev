#!/bin/bash
# setup_claude_opus_agent.sh - Version avec variables d'environnement GitHub
# Utilise UNIQUEMENT les secrets déjà configurés dans GitHub

set -e

echo "🚀 Configuration de Claude 4 Opus Agent pour JARVYS"
echo "================================================="

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "grok_orchestrator.py" ]; then
    echo -e "${RED}⚠️  Assurez-vous d'être dans /workspaces/appia-dev${NC}"
    exit 1
fi

# Afficher les variables d'environnement détectées
echo -e "\n${YELLOW}🔍 Détection des variables d'environnement GitHub...${NC}"

# Fonction pour vérifier une variable
check_env_var() {
    local var_name=$1
    if [ ! -z "${!var_name}" ]; then
        echo -e "${GREEN}✓${NC} $var_name détecté (${#var_name} caractères)"
        return 0
    else
        echo -e "${RED}✗${NC} $var_name non trouvé"
        return 1
    fi
}

# Vérifier toutes les variables
echo -e "\n${BLUE}Variables d'API:${NC}"
check_env_var "CLAUDE_API_KEY"
check_env_var "OPENAI_API_KEY"
check_env_var "GEMINI_API_KEY"
check_env_var "XAI_API_KEY"

echo -e "\n${BLUE}Variables GitHub:${NC}"
check_env_var "GH_TOKEN" || check_env_var "GITHUB_TOKEN"
check_env_var "GH_REPO"

echo -e "\n${BLUE}Variables Supabase:${NC}"
check_env_var "SUPABASE_URL"
check_env_var "SUPABASE_SERVICE_ROLE"
check_env_var "SUPABASE_KEY"
check_env_var "SUPABASE_ACCESS_TOKEN"
check_env_var "SUPABASE_PROJECT_ID"

echo -e "\n${BLUE}Variables GCP:${NC}"
check_env_var "GCP_SA_JSON"

# Créer un fichier .env qui référence les variables d'environnement
echo -e "\n${YELLOW}📝 Création du fichier .env...${NC}"

cat > .env << 'EOF'
# Ce fichier utilise les variables d'environnement GitHub/Codespaces
# Aucun secret n'est hardcodé ici

# API Keys - depuis les secrets GitHub
CLAUDE_API_KEY=${CLAUDE_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
GEMINI_API_KEY=${GEMINI_API_KEY}
XAI_API_KEY=${XAI_API_KEY}

# GitHub - utilise le token du Codespace
GH_TOKEN=${GH_TOKEN:-${GITHUB_TOKEN}}
GH_REPO=${GH_REPO:-yannabadie/appia-dev}
GH_REPO_DEV=${GH_REPO_DEV:-yannabadie/appia-dev}
GH_REPO_AI=${GH_REPO_AI:-yannabadie/appIA}

# Supabase - depuis les secrets GitHub
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_ROLE=${SUPABASE_SERVICE_ROLE}
SUPABASE_KEY=${SUPABASE_KEY}
SUPABASE_ACCESS_TOKEN=${SUPABASE_ACCESS_TOKEN}
SUPABASE_PROJECT_ID=${SUPABASE_PROJECT_ID}

# GCP
GCP_SA_JSON=${GCP_SA_JSON}

# Configuration par défaut
DAILY_COST_LIMIT=${DAILY_COST_LIMIT:-3.0}
CHECK_INTERVAL=${CHECK_INTERVAL:-300}
MAX_TASKS_PER_CYCLE=${MAX_TASKS_PER_CYCLE:-3}

# Secret Access Token (si disponible)
SECRET_ACCESS_TOKEN=${SECRET_ACCESS_TOKEN}
EOF

echo -e "${GREEN}✅ Fichier .env créé (utilise les variables d'environnement)${NC}"

# Mettre à jour claude_autonomous_agent.py
echo -e "\n${YELLOW}🤖 Mise à jour du modèle Claude 4 Opus...${NC}"

if [ -f "claude_autonomous_agent.py" ]; then
    # Remplacer par le bon modèle Claude 4 Opus
    sed -i 's/claude-3-opus-20240229/claude-opus-4-20250514/g' claude_autonomous_agent.py
    echo -e "${GREEN}✅ Modèle mis à jour: claude-opus-4-20250514${NC}"
else
    echo -e "${RED}⚠️  Fichier claude_autonomous_agent.py non trouvé${NC}"
fi

# Créer un script de test pour vérifier les variables
echo -e "\n${YELLOW}🧪 Création du script de test...${NC}"

cat > test_env_vars.py << 'EOF'
#!/usr/bin/env python3
"""
Test des variables d'environnement GitHub
"""
import os
from dotenv import load_dotenv

# Charger le .env (qui référence les variables d'environnement)
load_dotenv()

print("🔍 Test des Variables d'Environnement")
print("=" * 50)

# Variables à tester
vars_to_check = [
    "CLAUDE_API_KEY",
    "OPENAI_API_KEY", 
    "GEMINI_API_KEY",
    "XAI_API_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE",
    "SUPABASE_KEY"
]

print("\n📋 Résultats:")
for var in vars_to_check:
    value = os.getenv(var)
    if value:
        # Masquer partiellement la valeur
        masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: Non trouvé")

# Test spécifique pour Claude
claude_key = os.getenv("CLAUDE_API_KEY")
if claude_key and claude_key.startswith("sk-ant-"):
    print("\n✅ CLAUDE_API_KEY semble valide")
else:
    print("\n⚠️  CLAUDE_API_KEY manquante ou invalide")
    print("   Ajoutez-la dans les secrets GitHub de votre Codespace")
EOF

chmod +x test_env_vars.py

# Créer le script de lancement qui utilise les variables d'environnement
cat > run_claude.sh << 'EOF'
#!/bin/bash
# Lance Claude avec les variables d'environnement GitHub

echo "🤖 Démarrage de Claude 4 Opus Agent..."

# Les variables sont déjà dans l'environnement, pas besoin de les charger
# Vérifier seulement que Claude API Key existe
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ CLAUDE_API_KEY non trouvée dans les variables d'environnement"
    echo ""
    echo "Pour ajouter la clé Claude:"
    echo "1. Allez dans Settings > Secrets > Codespaces"
    echo "2. Ajoutez CLAUDE_API_KEY avec votre clé"
    echo "3. Recréez le Codespace ou redémarrez-le"
    exit 1
fi

echo "✅ Variables d'environnement détectées"
echo "🚀 Lancement de l'agent..."

# Lancer avec Poetry
poetry run python claude_autonomous_agent.py
EOF

chmod +x run_claude.sh

# Script pour afficher comment ajouter des secrets
cat > add_secrets_help.sh << 'EOF'
#!/bin/bash
# Aide pour ajouter des secrets GitHub

echo "📚 Guide pour ajouter des secrets dans GitHub Codespaces"
echo "======================================================"
echo ""
echo "1. Allez sur: https://github.com/settings/codespaces"
echo ""
echo "2. Dans 'Repository secrets', ajoutez:"
echo "   - CLAUDE_API_KEY"
echo "   - Autres clés si nécessaire"
echo ""
echo "3. Les secrets seront disponibles comme variables d'environnement"
echo "   dans tous vos Codespaces"
echo ""
echo "4. Pour vérifier: echo \$CLAUDE_API_KEY"
echo ""
echo "Note: Les secrets sont masqués dans les logs pour la sécurité"
EOF

chmod +x add_secrets_help.sh

# Installer les dépendances
echo -e "\n${YELLOW}📦 Installation des dépendances...${NC}"

if command -v poetry &> /dev/null; then
    poetry add anthropic python-dotenv --quiet 2>/dev/null || true
else
    pip install anthropic python-dotenv
fi

# Résumé final
echo -e "\n${GREEN}✅ Configuration terminée!${NC}"
echo -e "\n${BLUE}📋 Résumé:${NC}"
echo "- Utilise les variables d'environnement GitHub (pas de secrets hardcodés)"
echo "- Modèle Claude 4 Opus: claude-opus-4-20250514"
echo "- Scripts créés: run_claude.sh, test_env_vars.py"

# Vérifier si CLAUDE_API_KEY existe
if [ -z "$CLAUDE_API_KEY" ]; then
    echo -e "\n${RED}⚠️  IMPORTANT: CLAUDE_API_KEY non détectée${NC}"
    echo "Exécutez: ./add_secrets_help.sh pour voir comment l'ajouter"
else
    echo -e "\n${GREEN}✅ CLAUDE_API_KEY détectée${NC}"
    echo "Vous pouvez lancer: ./run_claude.sh"
fi

echo -e "\n${BLUE}🚀 Commandes disponibles:${NC}"
echo "- Test des variables: poetry run python test_env_vars.py"
echo "- Lancer Claude: ./run_claude.sh"
echo "- Aide secrets: ./add_secrets_help.sh"