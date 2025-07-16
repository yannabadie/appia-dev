#!/bin/bash
# setup_claude_codespaces.sh
# Script d'installation adapté pour GitHub Codespaces

set -e

echo "🚀 Installation de Claude 4 Opus Agent pour JARVYS (Codespaces)"
echo "=========================================================="

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
WORKSPACE_DIR="/workspaces/appia-dev"
AGENT_DIR="$WORKSPACE_DIR/claude_agent"
PYTHON_CMD="python3"

# Vérifier qu'on est bien dans Codespaces
check_environment() {
    echo -e "\n${YELLOW}📋 Vérification de l'environnement...${NC}"
    
    if [ ! -d "/workspaces" ]; then
        echo -e "${RED}❌ Ce script doit être exécuté dans GitHub Codespaces${NC}"
        exit 1
    fi
    
    # Vérifier Python
    if ! command -v $PYTHON_CMD &> /dev/null; then
        echo -e "${RED}❌ Python 3 non trouvé${NC}"
        exit 1
    fi
    
    # Afficher la version Python
    echo -e "${BLUE}Python version: $($PYTHON_CMD --version)${NC}"
    
    # Vérifier Poetry (si utilisé dans le projet)
    if command -v poetry &> /dev/null; then
        echo -e "${BLUE}Poetry trouvé: $(poetry --version)${NC}"
        USE_POETRY=true
    else
        USE_POETRY=false
    fi
    
    echo -e "${GREEN}✅ Environnement Codespaces vérifié${NC}"
}

# Créer la structure dans le projet existant
create_structure() {
    echo -e "\n${YELLOW}📁 Création de la structure dans le projet...${NC}"
    
    cd $WORKSPACE_DIR
    
    # Créer les dossiers nécessaires
    mkdir -p claude_agent/{core,tools,workflows,configs}
    mkdir -p .github/workflows
    mkdir -p tests/claude_agent
    
    echo -e "${GREEN}✅ Structure créée dans $WORKSPACE_DIR${NC}"
}

# Installer/Mettre à jour les dépendances
install_dependencies() {
    echo -e "\n${YELLOW}🐍 Installation des dépendances...${NC}"
    
    cd $WORKSPACE_DIR
    
    if [ "$USE_POETRY" = true ]; then
        echo -e "${BLUE}Utilisation de Poetry...${NC}"
        
        # Ajouter les dépendances avec Poetry
        poetry add anthropic pygithub supabase aiofiles websockets python-dotenv
        poetry add --group dev pylint black mypy bandit safety pytest pytest-asyncio
        
    else
        echo -e "${BLUE}Utilisation de pip...${NC}"
        
        # S'assurer qu'on utilise le venv existant
        if [ -d ".venv" ]; then
            source .venv/bin/activate
        else
            $PYTHON_CMD -m venv .venv
            source .venv/bin/activate
        fi
        
        # Mettre à jour pip
        pip install --upgrade pip
        
        # Créer requirements pour Claude
        cat >> requirements.txt << EOF

# Claude Agent Dependencies
anthropic>=0.18.0
pygithub>=2.0.0
supabase>=2.0.0
aiofiles>=23.0.0
websockets>=12.0.0
python-dotenv>=1.0.0

# Dev dependencies
pylint>=3.0.0
black>=23.0.0
mypy>=1.0.0
bandit>=1.7.0
safety>=3.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
EOF
        
        pip install -r requirements.txt
    fi
    
    echo -e "${GREEN}✅ Dépendances installées${NC}"
}

# Installer l'agent Claude dans le projet
install_claude_agent() {
    echo -e "\n${YELLOW}🤖 Installation de l'agent Claude...${NC}"
    
    cd $AGENT_DIR
    
    # Créer __init__.py
    touch __init__.py
    touch core/__init__.py
    touch tools/__init__.py
    
    # Créer le fichier principal de l'agent
    cat > core/claude_opus_agent.py << 'EOF'
"""
Claude 4 Opus Agent pour JARVYS - Version Codespaces
"""
import os
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path

import anthropic
from github import Github
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClaudeOpusAgent:
    """Agent autonome Claude 4 Opus pour JARVYS"""
    
    def __init__(self):
        # Initialisation des clients
        self.claude = anthropic.AsyncAnthropic(
            api_key=os.getenv("CLAUDE_API_KEY", "")
        )
        self.github = Github(os.getenv("GH_TOKEN"))
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE")
        )
        
        # Configuration
        self.workspace_dir = Path("/workspaces/appia-dev")
        self.cost_limit_daily = float(os.getenv("DAILY_COST_LIMIT", "3.0"))
        self.current_costs = 0.0
        
    async def run_in_codespace(self):
        """Mode spécial pour Codespaces - exécution unique"""
        logger.info("🚀 Démarrage en mode Codespace")
        
        try:
            # Analyser le code actuel
            issues = await self.analyze_current_code()
            
            if issues:
                logger.info(f"📊 {len(issues)} problèmes détectés")
                
                # Prioriser et corriger
                for issue in issues[:3]:  # Max 3 corrections
                    await self.fix_issue(issue)
                
                # Créer un rapport
                await self.create_report(issues)
            else:
                logger.info("✅ Aucun problème détecté")
                
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            
    async def analyze_current_code(self) -> List[Dict[str, Any]]:
        """Analyser le code dans le workspace actuel"""
        issues = []
        
        # Scanner les fichiers Python
        for py_file in self.workspace_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Demander à Claude d'analyser
                response = await self.claude.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[{
                        "role": "user",
                        "content": f"""Analyse ce fichier Python et identifie les problèmes:
                        
Fichier: {py_file.relative_to(self.workspace_dir)}

```python
{content[:2000]}  # Limiter pour l'exemple
```

Retourne uniquement les problèmes critiques sous forme JSON."""
                    }]
                )
                
                # Parser la réponse
                try:
                    file_issues = json.loads(response.content[0].text)
                    for issue in file_issues.get("issues", []):
                        issue["file"] = str(py_file.relative_to(self.workspace_dir))
                        issues.append(issue)
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"Erreur analyse {py_file}: {e}")
                
        return issues
    
    async def fix_issue(self, issue: Dict[str, Any]):
        """Corriger un problème détecté"""
        logger.info(f"🔧 Correction: {issue.get('description', 'Issue')}")
        
        file_path = self.workspace_dir / issue["file"]
        
        try:
            # Lire le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Demander la correction à Claude
            response = await self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": f"""Corrige ce problème dans le code:
                    
Problème: {issue['description']}
Fichier: {issue['file']}

Code actuel:
```python
{content}
```

Retourne UNIQUEMENT le code corrigé complet."""
                }]
            )
            
            fixed_code = response.content[0].text
            
            # Créer une branche pour la correction
            branch_name = f"claude-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Sauvegarder dans une nouvelle branche
            os.system(f"git checkout -b {branch_name}")
            
            # Écrire le fichier corrigé
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            
            # Committer
            os.system(f"git add {file_path}")
            os.system(f'git commit -m "[Claude] Fix: {issue["description"][:50]}"')
            
            logger.info(f"✅ Correction appliquée dans la branche {branch_name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la correction: {e}")
    
    async def create_report(self, issues: List[Dict[str, Any]]):
        """Créer un rapport des analyses"""
        report_path = self.workspace_dir / "claude_analysis_report.md"
        
        report = f"""# 📊 Rapport d'Analyse Claude 4 Opus

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Environnement: GitHub Codespaces

## Résumé

- **Fichiers analysés**: {len(set(i['file'] for i in issues))}
- **Problèmes détectés**: {len(issues)}
- **Corrections appliquées**: {min(3, len(issues))}

## Détails des problèmes

"""
        
        for i, issue in enumerate(issues, 1):
            report += f"""
### {i}. {issue.get('type', 'Issue')} dans {issue['file']}

**Description**: {issue.get('description', 'N/A')}

**Sévérité**: {issue.get('severity', 'medium')}

---
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Rapport créé: {report_path}")
EOF
    
    # Créer le script de lancement pour Codespaces
    cat > run_analysis.py << 'EOF'
#!/usr/bin/env python3
"""
Lancer l'analyse Claude dans Codespaces
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.claude_opus_agent import ClaudeOpusAgent

async def main():
    print("🤖 Claude 4 Opus Agent - Analyse du projet")
    print("=" * 50)
    
    agent = ClaudeOpusAgent()
    await agent.run_in_codespace()
    
    print("\n✅ Analyse terminée!")
    print("Vérifiez les branches Git créées et le rapport claude_analysis_report.md")

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    chmod +x run_analysis.py
    
    echo -e "${GREEN}✅ Agent Claude installé${NC}"
}

# Configurer les variables d'environnement
setup_environment() {
    echo -e "\n${YELLOW}🔐 Configuration de l'environnement...${NC}"
    
    cd $WORKSPACE_DIR
    
    # Créer .env.example si n'existe pas
    if [ ! -f .env.example ]; then
        cat > .env.example << 'EOF'
# Claude Agent Configuration
CLAUDE_API_KEY=your_claude_api_key_here
GH_TOKEN=your_github_pat_token_here
SUPABASE_URL=https://kzcswopokvknxmxczilu.supabase.co
SUPABASE_SERVICE_ROLE=your_service_role_key_here

# Limites
DAILY_COST_LIMIT=3.0
MAX_TASKS_PER_CYCLE=3
EOF
    fi
    
    # Copier vers .env si n'existe pas
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Configurez vos clés API dans .env${NC}"
    fi
    
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
}

# Ajouter les workflows GitHub
setup_github_workflows() {
    echo -e "\n${YELLOW}🔄 Ajout des workflows GitHub...${NC}"
    
    cd $WORKSPACE_DIR
    
    # Workflow pour l'analyse automatique
    cat > .github/workflows/claude-analysis.yml << 'EOF'
name: Claude Code Analysis

on:
  push:
    branches: [main, develop, grok-evolution]
  pull_request:
    types: [opened, synchronize]
  workflow_dispatch:

jobs:
  analyze:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install anthropic pygithub supabase
      
      - name: Run Claude Analysis
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE: ${{ secrets.SUPABASE_SERVICE_ROLE }}
        run: |
          python claude_agent/run_analysis.py
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: claude-analysis-report
          path: claude_analysis_report.md
EOF
    
    echo -e "${GREEN}✅ Workflows GitHub ajoutés${NC}"
}

# Créer les commandes utilitaires
create_utilities() {
    echo -e "\n${YELLOW}🛠️ Création des utilitaires...${NC}"
    
    cd $WORKSPACE_DIR
    
    # Script pour lancer l'analyse
    cat > analyze_with_claude.sh << 'EOF'
#!/bin/bash
# Lancer une analyse Claude

echo "🤖 Lancement de l'analyse Claude..."

# Activer l'environnement virtuel si nécessaire
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Lancer l'analyse
python claude_agent/run_analysis.py

# Afficher les résultats
if [ -f "claude_analysis_report.md" ]; then
    echo ""
    echo "📊 Rapport d'analyse:"
    echo "===================="
    cat claude_analysis_report.md
fi
EOF
    
    chmod +x analyze_with_claude.sh
    
    # Ajouter au Makefile si existe
    if [ -f "Makefile" ]; then
        echo -e "\n# Claude Analysis" >> Makefile
        echo "claude-analyze:" >> Makefile
        echo -e "\t./analyze_with_claude.sh" >> Makefile
    fi
    
    echo -e "${GREEN}✅ Utilitaires créés${NC}"
}

# Tester l'installation
test_installation() {
    echo -e "\n${YELLOW}🧪 Test de l'installation...${NC}"
    
    cd $WORKSPACE_DIR
    
    # Vérifier les imports Python
    $PYTHON_CMD -c "import anthropic; print('✅ anthropic importé')" 2>/dev/null || echo "❌ Erreur import anthropic"
    $PYTHON_CMD -c "import github; print('✅ github importé')" 2>/dev/null || echo "❌ Erreur import github"
    $PYTHON_CMD -c "import supabase; print('✅ supabase importé')" 2>/dev/null || echo "❌ Erreur import supabase"
    
    # Vérifier la structure
    [ -d "claude_agent" ] && echo "✅ Dossier claude_agent créé" || echo "❌ Dossier claude_agent manquant"
    [ -f ".env" ] && echo "✅ Fichier .env présent" || echo "❌ Fichier .env manquant"
    
    echo -e "${GREEN}✅ Tests terminés${NC}"
}

# Afficher les instructions
show_instructions() {
    echo -e "\n${GREEN}🎉 Installation terminée!${NC}"
    echo -e "\n${YELLOW}📝 Prochaines étapes:${NC}"
    echo "1. Configurez vos clés API:"
    echo "   ${BLUE}nano .env${NC}"
    echo ""
    echo "2. Lancez une analyse:"
    echo "   ${BLUE}./analyze_with_claude.sh${NC}"
    echo ""
    echo "3. Configurez les secrets GitHub:"
    echo "   ${BLUE}gh secret set CLAUDE_API_KEY${NC}"
    echo ""
    echo -e "${YELLOW}💡 Commandes disponibles:${NC}"
    echo "- Analyse rapide: ${BLUE}python claude_agent/run_analysis.py${NC}"
    echo "- Avec Poetry: ${BLUE}poetry run python claude_agent/run_analysis.py${NC}"
    echo "- Via Make: ${BLUE}make claude-analyze${NC}"
    echo ""
    echo -e "${GREEN}✨ Claude 4 Opus est prêt dans votre Codespace!${NC}"
}

# Fonction principale
main() {
    echo -e "${BLUE}Installation dans: $WORKSPACE_DIR${NC}"
    echo -e "${YELLOW}Continuer? (O/n)${NC} "
    read -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Oo]$ ]] && [[ ! -z $REPLY ]]; then
        echo "Installation annulée"
        exit 0
    fi
    
    check_environment
    create_structure
    install_dependencies
    install_claude_agent
    setup_environment
    setup_github_workflows
    create_utilities
    test_installation
    show_instructions
}

# Lancer l'installation
main