# JARVYS Ecosystem - Agents DevOps Autonomes

**JARVYS_DEV** est un agent d'automatisation DevOps cloud-first qui s'exécute exclusivement sur GitHub Actions et GCP. Il collabore avec **JARVYS_AI** (local/hybride) via une mémoire infinie partagée sur Supabase.

## 🏗️ Architecture Cloud-First

### 🌩️ JARVYS_DEV (Cloud Seulement)
- **Environnement** : GitHub Actions exclusivement
- **Fonction** : Automatisation DevOps, CI/CD, monitoring
- **Exécution** : Cron toutes les heures + triggers événements
- **Interface** : Dashboard auto-hébergé sur Supabase

### 🏠 JARVYS_AI (Local/Hybride)  
- **Environnement** : Machine locale de l'utilisateur
- **Fonction** : Assistance développement, analyse code
- **Communication** : API et mémoire partagée Supabase
- **Interface** : CLI et intégrations IDE

### 🧠 Mémoire Infinie Partagée
- **Support** : Supabase avec recherche vectorielle
- **Capacité** : Stockage illimité des interactions/préférences
- **Persistance** : Tout est mémorisé sur l'utilisateur
- **Recherche** : Sémantique via embeddings OpenAI

## 🚀 Démarrage Rapide

### 1. Dashboard Auto-hébergé (Supabase)

Le dashboard est automatiquement déployé sur Supabase Edge Functions :

```bash
# Accédez au dashboard
# URL fournie après déploiement via GitHub Actions
https://[votre-projet].supabase.co/functions/v1/dashboard
```

**Fonctionnalités** :
- � Métriques en temps réel (coûts, performances)
- � Interface de recherche dans la mémoire infinie  
- 🤖 État des agents (JARVYS_DEV cloud + JARVYS_AI local)
- 📈 Historique et analytics

### 2. Configuration Cloud (GitHub Secrets)

Définissez ces secrets dans votre repository GitHub :

```yaml
# Secrets requis pour JARVYS_DEV (cloud)
OPENAI_API_KEY: "sk-..."
GITHUB_TOKEN: "ghp_..."  
SUPABASE_URL: "https://xxx.supabase.co"
SUPABASE_KEY: "eyJ..."
SUPABASE_PROJECT_REF: "xxx"
SUPABASE_ACCESS_TOKEN: "sbp_..."
GEMINI_API_KEY: "AIza..."
GCP_SA_JSON: '{"type": "service_account"...}'
```

### 3. Activation Agent Cloud

```bash
# L'agent JARVYS_DEV se lance automatiquement sur GitHub Actions
# Triggers : push, pull_request, schedule (toutes les heures)

# Déclencher manuellement
gh workflow run "🌩️ JARVYS_DEV Cloud Deployment" \
  --field mode=autonomous
```

## 🛠️ Développement Local (JARVYS_AI)

Pour développer et tester JARVYS_AI en local :

```bash
# 1. Installation des dépendances
poetry install --with dev

# 2. Configuration environnement local
export OPENAI_API_KEY="sk-..."
export SUPABASE_URL="https://xxx.supabase.co"  
export SUPABASE_KEY="eyJ..."

# 3. Test de la mémoire partagée
poetry run python src/jarvys_dev/tools/memory_infinite.py

# 4. Lancement JARVYS_AI local (à développer)
# poetry run python jarvys_ai/main.py
```

## 🔧 Communication Inter-Agents

### JARVYS_DEV → JARVYS_AI
- **Issues GitHub** avec label `from_jarvys_dev`
- **Mémoire partagée** : Contexte et préférences utilisateur
- **APIs** : Endpoints spécifiques pour coordination

### JARVYS_AI → JARVYS_DEV  
- **Issues GitHub** avec label `from_jarvys_ai`
- **Mémoire partagée** : Retours et apprentissages
- **Pull Requests** : Propositions de code

## 📊 Dashboard Auto-hébergé

### Architecture Supabase
- **Edge Functions** : Interface web responsive
- **Base vectorielle** : Mémoire infinie avec recherche sémantique
- **Real-time** : Mises à jour WebSocket automatiques
- **RLS** : Sécurité par utilisateur

### Métriques Trackées
- 💰 **Coûts API** : OpenAI, Gemini, GitHub API calls
- ⚡ **Performance** : Temps de réponse, taux de succès
- 🧠 **Mémoire** : Utilisation, recherches, importance
- 🤖 **Agents** : Status, heartbeat, activité

## 🔍 Fonctionnalités Avancées

### Mémoire Infinie
```python
from src.jarvys_dev.tools.memory_infinite import get_memory

# Mémoriser une préférence utilisateur
memory = get_memory("JARVYS_DEV", "user_123")
memory.memorize(
    "L'utilisateur préfère les solutions simples et épurées",
    memory_type="preference", 
    importance_score=0.9
)

# Rechercher dans la mémoire
results = memory.recall("préférences design interface")
```

### Auto-déploiement
- **GitHub Actions** : Déploiement automatique dashboard
- **Supabase CLI** : Edge Functions et schéma DB
- **Monitoring** : Health checks et alerting

## Exécution des tests

```bash
poetry run pytest -q
```

## Documentation

La documentation est générée **automatiquement** et publiée sur le Wiki GitHub
lors des modifications du code source.

### Générer la documentation localement

```bash
python scripts/generate_wiki_docs.py
```

### Documentation MkDocs (alternative)

```bash
poetry run mkdocs serve
```

Un workflow automatique met à jour le Wiki GitHub lors des pushes sur `main` ou `dev`.

## Utilisation

### Lancement manuel de la boucle autonome

```bash
poetry run python -m jarvys_dev.langgraph_loop
```

### Serveur MCP (Model Context Protocol)

Le serveur MCP permet l'intégration avec d'autres outils via le protocole Model Context Protocol :

```bash
poetry run uvicorn app.main:app --port 54321
```

**Endpoints disponibles** :
- `GET /` - Status du serveur
- `GET /v1/tool-metadata` - Métadonnées MCP
- `POST /v1/tool-invocations/ask_llm` - Invocation LLM

### Bootstrap du projet

Pour initialiser un nouveau projet avec la structure complète :

```bash
poetry run python bootstrap_jarvys_dev.py
```

## Model watcher

Le `model_watcher` surveille les nouveaux modèles LLM d'OpenAI, Anthropic et
Google Gemini. Quand un nouveau modèle est disponible, il met à jour
`src/jarvys_dev/model_config.json` et ouvre une issue GitHub.

Exécution manuelle :

```bash
poetry run python -m jarvys_dev.model_watcher
```

Le workflow `model-detection.yml` exécute cette tâche quotidiennement.
Configurez les secrets `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` et
`GH_TOKEN` dans les paramètres de votre repository.

## 📊 Dashboard et Monitoring

JARVYS_DEV inclut un dashboard complet pour le monitoring et l'interaction :

### Fonctionnalités du Dashboard

- **Métriques en temps réel** : Coûts API, nombre d'appels, temps de réponse
- **Chat interactif** : Communiquez directement avec l'agent
- **Activité en direct** : Suivi des tâches et actions de l'agent
- **Contrôles** : Pause, redémarrage, analyse manuelle
- **WebSocket** : Mises à jour automatiques sans rechargement

### Accès au Dashboard

```bash
# Avec le démarrage complet
python start_jarvys.py

# Ou dashboard seul
python start_jarvys.py --component dashboard

# Interface disponible sur: http://localhost:8080
```

## 🔍 Introspection et Auto-amélioration

L'agent peut s'auto-analyser et proposer des améliorations :

```bash
# Lance une session d'introspection complète
python scripts/introspection.py

# L'agent va :
# - Analyser sa propre architecture
# - Identifier les points d'amélioration
# - Proposer une roadmap d'évolution
# - Générer des suggestions d'auto-amélioration
```

### Capacités d'Introspection

- **Analyse architecturale** : Qualité du code, tests, dépendances
- **Auto-questionnement** : L'agent se pose des questions sur ses performances
- **Génération de roadmap** : Plan d'amélioration priorisé
- **Suggestions d'évolution** : Idées pour devenir plus autonome

## Workflows automatisés

- **CI** (`ci.yml`) : Tests automatiques sur push/PR
- **Model Detection** (`model-detection.yml`) : Veille quotidienne des nouveaux modèles
- **Wiki Documentation** (`wiki-sync.yml`) : Génération automatique de documentation
- **Agent** (`agent.yml`) : Orchestration des tâches autonomes

## Service account key

Le fichier `gcp-sa.json` n'est pas suivi dans le dépôt.
Fournissez son contenu via la variable `GCP_SA_JSON`.

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier [`LICENSE`](LICENSE).
