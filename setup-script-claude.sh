#!/bin/bash
# setup_claude_opus_agent.sh
# Script d'installation complet pour Claude 4 Opus Agent dans JARVYS

set -e

echo "🚀 Installation de Claude 4 Opus Agent pour JARVYS"
echo "================================================"

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier les prérequis
check_requirements() {
    echo -e "\n${YELLOW}📋 Vérification des prérequis...${NC}"
    
    # Python 3.11+
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 non installé${NC}"
        exit 1
    fi
    
    # Git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git non installé${NC}"
        exit 1
    fi
    
    # Node.js pour l'extension VS Code
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}⚠️  Node.js non installé (requis pour l'extension VS Code)${NC}"
    fi
    
    echo -e "${GREEN}✅ Prérequis vérifiés${NC}"
}

# Créer la structure des dossiers
create_structure() {
    echo -e "\n${YELLOW}📁 Création de la structure...${NC}"
    
    # Dossier principal
    mkdir -p ~/jarvys-claude-agent/{agent,extension,workflows,configs}
    
    cd ~/jarvys-claude-agent
    
    echo -e "${GREEN}✅ Structure créée${NC}"
}

# Installer les dépendances Python
install_python_deps() {
    echo -e "\n${YELLOW}🐍 Installation des dépendances Python...${NC}"
    
    # Créer un environnement virtuel
    python3 -m venv venv
    source venv/bin/activate
    
    # Mettre à jour pip
    pip install --upgrade pip
    
    # Installer les dépendances
    cat > requirements.txt << EOF
anthropic>=0.18.0
openai>=1.0.0
google-generativeai>=0.3.0
supabase>=2.0.0
pygithub>=2.0.0
langchain>=0.1.0
langchain-community>=0.1.0
langgraph>=0.0.20
aiofiles>=23.0.0
websockets>=12.0.0
python-dotenv>=1.0.0
pylint>=3.0.0
black>=23.0.0
mypy>=1.0.0
bandit>=1.7.0
safety>=3.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
EOF
    
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ Dépendances Python installées${NC}"
}

# Configurer les variables d'environnement
setup_environment() {
    echo -e "\n${YELLOW}🔐 Configuration des variables d'environnement...${NC}"
    
    cat > .env.template << 'EOF'
# API Keys
CLAUDE_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
XAI_API_KEY=your_xai_api_key_here

# GitHub
GH_TOKEN=your_github_pat_token_here
GH_REPO_DEV=yannabadie/appia-dev
GH_REPO_AI=yannabadie/appIA

# Supabase
SUPABASE_URL=https://kzcswopokvknxmxczilu.supabase.co
SUPABASE_SERVICE_ROLE=your_service_role_key_here
SUPABASE_KEY=your_anon_key_here

# Configuration
DAILY_COST_LIMIT=3.0
CHECK_INTERVAL=300
MAX_TASKS_PER_CYCLE=3
EOF
    
    if [ ! -f .env ]; then
        cp .env.template .env
        echo -e "${YELLOW}⚠️  Veuillez configurer vos clés API dans le fichier .env${NC}"
    fi
    
    echo -e "${GREEN}✅ Template d'environnement créé${NC}"
}

# Installer l'agent Claude
install_claude_agent() {
    echo -e "\n${YELLOW}🤖 Installation de l'agent Claude...${NC}"
    
    cd agent
    
    # Copier le code de l'agent
    cat > claude_autonomous_agent.py << 'EOF'
# Code de l'agent depuis l'artifact claude-agent-jarvys
# [Le code complet sera copié ici]
EOF
    
    # Créer le script de lancement
    cat > run_agent.py << 'EOF'
#!/usr/bin/env python3
"""
Launcher pour Claude 4 Opus Agent
"""
import asyncio
import sys
import os
from pathlib import Path

# Ajouter le parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_autonomous_agent import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Agent arrêté par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
EOF
    
    chmod +x run_agent.py
    
    echo -e "${GREEN}✅ Agent Claude installé${NC}"
}

# Configurer l'extension VS Code
setup_vscode_extension() {
    echo -e "\n${YELLOW}🧩 Configuration de l'extension VS Code...${NC}"
    
    cd ../extension
    
    # Package.json pour l'extension
    cat > package.json << 'EOF'
{
  "name": "claude-opus-agent",
  "displayName": "Claude 4 Opus Agent",
  "description": "Agent autonome Claude 4 Opus pour JARVYS",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["Other"],
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "claude-opus.toggle",
        "title": "Claude Opus: Basculer connexion"
      },
      {
        "command": "claude-opus.fixCurrentFile",
        "title": "Claude Opus: Corriger le fichier actuel"
      },
      {
        "command": "claude-opus.analyzeProject",
        "title": "Claude Opus: Analyser le projet"
      },
      {
        "command": "claude-opus.showLogs",
        "title": "Claude Opus: Afficher les logs"
      },
      {
        "command": "claude-opus.createIssue",
        "title": "Claude Opus: Créer une issue GitHub"
      },
      {
        "command": "claude-opus.watchMode",
        "title": "Claude Opus: Mode surveillance"
      }
    ],
    "configuration": {
      "title": "Claude Opus Agent",
      "properties": {
        "claude-opus.apiKey": {
          "type": "string",
          "default": "",
          "description": "Clé API Claude"
        },
        "claude-opus.githubToken": {
          "type": "string",
          "default": "",
          "description": "Token GitHub"
        },
        "claude-opus.supabaseUrl": {
          "type": "string",
          "default": "",
          "description": "URL Supabase"
        },
        "claude-opus.supabaseKey": {
          "type": "string",
          "default": "",
          "description": "Clé Supabase"
        },
        "claude-opus.pythonPath": {
          "type": "string",
          "default": "python3",
          "description": "Chemin vers Python"
        },
        "claude-opus.agentPath": {
          "type": "string",
          "default": "",
          "description": "Chemin vers l'agent Claude"
        }
      }
    },
    "keybindings": [
      {
        "command": "claude-opus.fixCurrentFile",
        "key": "ctrl+alt+f",
        "mac": "cmd+alt+f"
      },
      {
        "command": "claude-opus.analyzeProject",
        "key": "ctrl+alt+a",
        "mac": "cmd+alt+a"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.x",
    "typescript": "^5.3.0"
  },
  "dependencies": {
    "ws": "^8.16.0"
  }
}
EOF
    
    # tsconfig.json
    cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2022",
    "outDir": "out",
    "lib": ["ES2022"],
    "sourceMap": true,
    "rootDir": "src",
    "strict": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
EOF
    
    # Créer le dossier src et copier l'extension
    mkdir -p src
    # Le code TypeScript de l'extension sera copié ici
    
    echo -e "${GREEN}✅ Extension VS Code configurée${NC}"
}

# Configurer les workflows GitHub
setup_github_workflows() {
    echo -e "\n${YELLOW}🔄 Configuration des workflows GitHub...${NC}"
    
    cd ../workflows
    
    # Copier les workflows
    cp ~/jarvys-claude-agent/workflows/* .
    
    echo -e "${GREEN}✅ Workflows GitHub configurés${NC}"
    echo -e "${YELLOW}ℹ️  Copiez le dossier workflows dans .github/workflows de vos repos${NC}"
}

# Créer les tables Supabase
setup_supabase() {
    echo -e "\n${YELLOW}🗄️ Configuration de Supabase...${NC}"
    
    cd ../configs
    
    cat > supabase_schema.sql << 'EOF'
-- Tables pour Claude 4 Opus Agent

-- Table des logs
CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    agent TEXT NOT NULL,
    activity TEXT NOT NULL,
    status TEXT,
    costs DECIMAL(10, 4) DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    error_message TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table des fixes en attente
CREATE TABLE IF NOT EXISTS pending_fixes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    repo TEXT NOT NULL,
    branch_name TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    issue_description TEXT,
    file_path TEXT,
    pr_created BOOLEAN DEFAULT FALSE,
    pr_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table des suggestions d'amélioration
CREATE TABLE IF NOT EXISTS improvement_suggestions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    suggestions TEXT,
    agent TEXT,
    implemented BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour les performances
CREATE INDEX idx_agent_logs_timestamp ON agent_logs(timestamp);
CREATE INDEX idx_agent_logs_agent ON agent_logs(agent);
CREATE INDEX idx_pending_fixes_repo ON pending_fixes(repo);
CREATE INDEX idx_pending_fixes_pr_created ON pending_fixes(pr_created);

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ language 'plpgsql';

-- Trigger pour pending_fixes
CREATE TRIGGER update_pending_fixes_updated_at BEFORE UPDATE
    ON pending_fixes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vue pour le monitoring
CREATE VIEW agent_activity_summary AS
SELECT 
    DATE(timestamp) as date,
    agent,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed_runs,
    SUM(costs) as total_costs,
    SUM(tasks_completed) as total_tasks
FROM agent_logs
GROUP BY DATE(timestamp), agent
ORDER BY date DESC, agent;
EOF
    
    echo -e "${GREEN}✅ Schéma Supabase créé${NC}"
    echo -e "${YELLOW}ℹ️  Exécutez ce SQL dans votre dashboard Supabase${NC}"
}

# Créer les scripts de démarrage
create_launchers() {
    echo -e "\n${YELLOW}🚀 Création des scripts de lancement...${NC}"
    
    cd ~/jarvys-claude-agent
    
    # Script de démarrage principal
    cat > start_claude_agent.sh << 'EOF'
#!/bin/bash
# Démarrer Claude 4 Opus Agent

echo "🤖 Démarrage de Claude 4 Opus Agent..."

# Charger l'environnement
source venv/bin/activate
source .env

# Démarrer l'agent
cd agent
python run_agent.py
EOF
    
    chmod +x start_claude_agent.sh
    
    # Service systemd (optionnel)
    cat > claude-agent.service << 'EOF'
[Unit]
Description=Claude 4 Opus Agent for JARVYS
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/jarvys-claude-agent
ExecStart=/home/$USER/jarvys-claude-agent/start_claude_agent.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    echo -e "${GREEN}✅ Scripts de lancement créés${NC}"
}

# Afficher les instructions finales
show_instructions() {
    echo -e "\n${GREEN}🎉 Installation terminée!${NC}"
    echo -e "\n${YELLOW}📝 Prochaines étapes:${NC}"
    echo "1. Configurez vos clés API dans .env"
    echo "2. Créez les tables Supabase avec configs/supabase_schema.sql"
    echo "3. Copiez les workflows dans vos repos GitHub"
    echo "4. Installez l'extension VS Code:"
    echo "   cd extension && npm install && npm run compile"
    echo "5. Démarrez l'agent: ./start_claude_agent.sh"
    echo -e "\n${YELLOW}🔧 Commandes utiles:${NC}"
    echo "- Démarrer l'agent: ./start_claude_agent.sh"
    echo "- Voir les logs: tail -f agent/logs/claude.log"
    echo "- Installer comme service: sudo cp claude-agent.service /etc/systemd/system/"
    echo -e "\n${GREEN}✨ Claude 4 Opus est prêt à améliorer JARVYS!${NC}"
}

# Fonction principale
main() {
    echo "Dossier d'installation: ~/jarvys-claude-agent"
    read -p "Continuer? (O/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Oo]$ ]] && [[ ! -z $REPLY ]]; then
        echo "Installation annulée"
        exit 1
    fi
    
    check_requirements
    create_structure
    install_python_deps
    setup_environment
    install_claude_agent
    setup_vscode_extension
    setup_github_workflows
    setup_supabase
    create_launchers
    show_instructions
}

# Lancer l'installation
main
