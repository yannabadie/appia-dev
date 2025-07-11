#!/bin/bash
# 🚀 Script de déploiement JARVYS_AI pour appIA

set -e

echo "🚀 Déploiement JARVYS_AI dans le repo appIA"
echo "============================================"

# Vérifier les prérequis
command -v gh >/dev/null 2>&1 || { echo "❌ GitHub CLI requis. Installation: https://cli.github.com/"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git requis."; exit 1; }

# Configuration
REPO_NAME="yannabadie/appIA"
SOURCE_DIR="appIA_complete_package"

echo "📋 Repository cible: $REPO_NAME"
echo "📁 Source: $SOURCE_DIR"

# Vérifier l'authentification GitHub
if ! gh auth status >/dev/null 2>&1; then
    echo "🔐 Authentification GitHub CLI requise"
    gh auth login
fi

# Vérifier si le repo existe
if ! gh repo view "$REPO_NAME" >/dev/null 2>&1; then
    echo "📝 Création du repository $REPO_NAME"
    gh repo create "$REPO_NAME" --public --description "🤖 JARVYS_AI - Agent Local Autonome pour optimisation continue"
fi

# Cloner le repo (ou l'initialiser s'il est vide)
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

if gh repo clone "$REPO_NAME" . 2>/dev/null; then
    echo "📥 Repository cloné"
else
    echo "🆕 Initialisation nouveau repository"
    git init
    git remote add origin "https://github.com/$REPO_NAME.git"
    git branch -M main
fi

# Copier tous les fichiers du package
echo "📦 Copie des fichiers JARVYS_AI..."
cp -r "$OLDPWD"/* .

# Vérifier la structure
echo "📋 Structure créée:"
find . -type f -name "*.py" -o -name "*.yml" -o -name "*.md" -o -name "*.txt" | head -20

# Git add et commit
git add .
git config user.name "JARVYS_DEV" 2>/dev/null || true
git config user.email "jarvys@appia-dev.ai" 2>/dev/null || true

if git diff --staged --quiet; then
    echo "ℹ️  Aucun changement à commiter"
else
    git commit -m "🤖 JARVYS_AI - Déploiement initial complet

🚀 Agent local autonome avec:
- Workflows GitHub Actions automatisés
- Intégration complète JARVYS_DEV  
- Dashboard Supabase partagé
- Optimisation continue des coûts
- Auto-amélioration par IA

Version: 1.0.0
Date: $(date)"
fi

# Push vers GitHub
echo "📤 Push vers GitHub..."
git push -u origin main

echo ""
echo "✅ Déploiement JARVYS_AI terminé avec succès!"
echo "🔗 Repository: https://github.com/$REPO_NAME"
echo "🔧 Actions: https://github.com/$REPO_NAME/actions"
echo "📊 Dashboard: https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/"
echo ""
echo "🔄 Prochaines étapes:"
echo "1. Les workflows GitHub Actions sont automatiquement activés"
echo "2. Les secrets sont synchronisés depuis JARVYS_DEV"  
echo "3. JARVYS_AI commencera à traiter les issues sous 30 minutes"
echo "4. Surveillance des coûts et optimisations automatiques actives"

# Cleanup
rm -rf "$TEMP_DIR"
