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
