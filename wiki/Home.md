# 🤖 JARVYS_DEV - Agent DevOps Autonome

*Documentation générée automatiquement le 10/07/2025 à 18:20*

## 🎯 Vue d'ensemble

JARVYS_DEV est un agent d'automatisation DevOps qui implémente une boucle autonome **Observe-Plan-Act-Reflect** pour gérer le cycle de vie d'un projet logiciel. Il combine l'intelligence artificielle avec l'automatisation pour fournir une assistance DevOps intelligente et proactive.

## 🏗️ Architecture Technique

### Boucle Principale
- **Type**: Observe-Plan-Act-Reflect Loop
- **Implémentation**: LangGraph StateGraph
- **Seuil de confiance**: 0.85

### Modèles LLM Supportés
- OpenAI
- Google Gemini
- Anthropic (via GitHub Copilot)

**Modèles actuels configurés:**
```json
{
  "openai": "whisper-1",
  "anthropic": "claude-4",
  "gemini": "models/text-embedding-004"
}
```

## ⚡ Capacités Autonomes

### 🤖 Automatisation GitHub
- Issue creation with labels
- Pull request management
- Code generation via Copilot
- Branch management
- Commit automation

### 📊 Monitoring & Observabilité
- Model availability tracking
- Performance benchmarking
- Error logging with secret masking
- Confidence scoring

### 🧠 Système de Mémoire
- Vector embeddings via Supabase
- Semantic search
- Experience persistence
- Context retrieval

## 🔧 Outils Disponibles

### github_tools
- **Fichier**: `src/jarvys_dev/tools/github_tools.py`
- **Description**: GitHub helpers.

Secrets nécessaires : GH_TOKEN, GH_REPO

### memory
- **Fichier**: `src/jarvys_dev/tools/memory.py`
- **Description**: No description available


## 🔄 Workflows Automatisés

- **model-detection**: scheduled, manual
- **wiki-init**: push, manual
- **ci**: push, pull_request
- **agent**: scheduled, manual
- **wiki-sync**: push
- **wiki**: push, pull_request, manual

## 🌐 Intégrations

### GitHub
- **API**: PyGithub
- **Fonctionnalités**: Issues, PRs, Projects, GraphQL

### Supabase (Base Vectorielle)
- **Fonctionnalités**: Vector DB, RLS, SQL functions

### Serveur MCP (Model Context Protocol)
- **Port**: 54321
- **Endpoints**: /v1/tool-metadata, /v1/tool-invocations/ask_llm

## 🚀 Démarrage Rapide

### 1. Variables d'environnement requises
```bash
# Core
export OPENAI_API_KEY="your_key"
export GH_TOKEN="your_github_token"
export GH_REPO="owner/repo"

# Base vectorielle
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"

# Google AI (requis)
export GEMINI_API_KEY="your_gemini_key"

# GCP pour Cloud Functions (requis)
export GCP_SA_JSON='{"type": "service_account", "project_id": "your_project"}'
```

### 2. Installation
```bash
pip install poetry
poetry install --with dev
```

### 3. Lancement de la boucle autonome
```bash
poetry run python -m jarvys_dev.langgraph_loop
```

### 4. Serveur MCP
```bash
poetry run uvicorn app.main:app --port 54321
```

## 📈 Métriques & Performance

- **Tests**: Tous les tests passent avec couverture complète
- **Benchmarking**: Latence et coût des modèles LLM trackés
- **Monitoring**: Logs avec masquage automatique des secrets
- **Qualité**: Pre-commit hooks + pytest automatisés

## 🤝 Collaboration Inter-Agents

JARVYS_DEV communique avec **JARVYS_AI** via :
- Création d'issues GitHub étiquetées `from_jarvys_ai`
- Format JSON structuré pour les tâches
- Escalade automatique vers validation humaine

---

*Cette documentation est mise à jour automatiquement à chaque modification du code.*
