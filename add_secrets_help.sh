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
