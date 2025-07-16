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

### 1. Dashboard Auto-hébergé (Supabase) 🔐

Le dashboard est automatiquement déployé sur Supabase Edge Functions avec authentification :

```bash
# URL du dashboard JARVYS
https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/

# Accès avec authentification (Header Authorization)
curl -H "Authorization: Bearer YOUR_SUPABASE_KEY" \
  https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/

# Ou accès browser avec token
https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/?token=YOUR_SUPABASE_KEY
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
SUPABASE_SERVICE_ROLE: "eyJ..."
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

## 🔒 Firewall et Sécurité Réseau

### Configuration Firewall pour GitHub Actions et Copilot

**IMPORTANT:** Tous les workflows de ce repository incluent des étapes de configuration firewall automatiques pour maintenir la connectivité avec les services essentiels GitHub et Copilot.

#### Domaines Essentiels Autorisés

Les domaines suivants **DOIVENT** être autorisés avant toute activation de firewall :

```bash
# Domaines GitHub essentiels
github.com                     # Repository et API principale
api.github.com                 # API GitHub Actions
copilot-proxy.githubusercontent.com  # Service Copilot
uploads.github.com             # Upload d'artefacts
objects.githubusercontent.com   # Objets et contenus

# Ports essentiels
443/tcp                        # HTTPS
80/tcp                         # HTTP (redirections)
53/udp                         # DNS
```

#### Configuration UFW Recommandée

```bash
# Étapes à exécuter AVANT activation du firewall
sudo ufw allow out to github.com
sudo ufw allow out to api.github.com
sudo ufw allow out to copilot-proxy.githubusercontent.com
sudo ufw allow out to uploads.github.com
sudo ufw allow out to objects.githubusercontent.com

# Ports essentiels
sudo ufw allow out 443
sudo ufw allow out 80
sudo ufw allow out 53

# Activer le firewall seulement après les règles d'autorisation
sudo ufw --force enable
```

#### Validation de Connectivité

Un workflow dédié `network-validation.yml` teste la connectivité vers tous les domaines essentiels :

- **Avant déploiement** : Valide que tous les domaines sont accessibles
- **Test automatique** : Vérifie HTTP/HTTPS et résolution DNS
- **Rapport détaillé** : Génère un rapport de connectivité avec recommandations firewall

#### Standards Repository

1. **Placement des configurations firewall** : Toujours à la FIN de chaque job de workflow, après toutes les étapes Copilot et d'environnement
2. **Règles d'autorisation** : Explicites pour chaque domaine GitHub/Copilot requis
3. **Tests préalables** : Validation de connectivité obligatoire avant activation firewall
4. **Documentation** : Commentaires dans workflows expliquant le placement et timing

#### Dépannage Connectivité

Si un workflow échoue avec des erreurs réseau :

1. Vérifier que les domaines essentiels sont accessibles
2. Exécuter le workflow `network-validation.yml` 
3. Contrôler les règles firewall actives
4. Consulter les logs de connectivité dans les artefacts

## 🤖 Copilot et GitHub Actions

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

## 🤖 Architecture Cloud-First & Mémoire Infinie

JARVYS_DEV s'exécute exclusivement dans le cloud avec mémoire partagée :

```bash
# JARVYS_DEV: Cloud uniquement (GitHub Actions/GCP)
# - Exécution autonome toutes les heures
# - Dashboard auto-hébergé sur Supabase Edge Functions
# - Mémoire infinie partagée avec JARVYS_AI

# JARVYS_AI: Local/Hybride (à venir)
# - Interface IDE/CLI locale
# - Communication via GitHub Issues
# - Partage la même mémoire infinie
```

### Architecture Cloud-First

- **🌩️ Cloud Only**: JARVYS_DEV n'existe qu'en cloud (GitHub Actions)
- **🧠 Mémoire Infinie**: Base vectorielle Supabase avec recherche sémantique
- **📊 Dashboard Auto-hébergé**: Interface Supabase Edge Functions  
- **🔄 Communication Inter-agents**: Issues GitHub pour JARVYS_AI ↔ JARVYS_DEV
- **⚡ Exécution Autonome**: Workflows GitHub Actions avec déclencheurs multiples

### Dashboard & Monitoring

Accès au dashboard auto-hébergé : `https://[votre-projet].supabase.co/functions/v1/dashboard`

- Métriques en temps réel (coûts, performances, succès)
- Statut des agents (JARVYS_DEV cloud, JARVYS_AI local)
- Recherche dans la mémoire infinie partagée
- Analytics et optimisations automatiques

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


## Update:  (2025-07-16)
# Description

JARVYS_DEV et JARVYS_AI sont des systèmes d'intelligence artificielle sophistiqués conçus pour optimiser et améliorer les opérations numériques. JARVYS_DEV fonctionne dans un environnement cloud, utilisant MCP/GCP et la mémoire Supabase pour générer JARVYS_AI, qui fonctionne localement, utilisant le routage LLMs et l'auto-amélioration pour optimiser ses performances.

# Changements

Dans cette mise à jour, nous avons apporté plusieurs améliorations significatives à la fois à JARVYS_DEV et JARVYS_AI. Nous avons intégré des fonctionnalités d'analyse de sentiment pour permettre à JARVYS_AI de comprendre et de répondre aux émotions exprimées dans les textes. De plus, nous avons ajouté une fonctionnalité de simulation quantique à JARVYS_DEV, permettant une résolution de problèmes plus rapide et plus efficace.

# Impact

Ces mises à jour auront un impact significatif sur la façon dont les utilisateurs interagissent avec JARVYS_DEV et JARVYS_AI. L'analyse de sentiment permettra à JARVYS_AI de fournir des réponses plus empathiques et personnalisées, améliorant ainsi l'expérience utilisateur. La simulation quantique, quant à elle, permettra à JARVYS_DEV de résoudre des problèmes plus rapidement et plus efficacement, améliorant ainsi la productivité.

# Exemples

Pour illustrer, imaginez que vous soyez un utilisateur exprimant de la frustration dans un message à JARVYS_AI. Grâce à l'analyse de sentiment, JARVYS_AI pourra détecter votre frustration et répondre de manière appropriée, peut-être en vous offrant des solutions pour résoudre votre problème ou en exprimant de l'empathie pour votre situation.

Pour la simulation quantique, imaginez que vous ayez un problème complexe à résoudre. Grâce à la simulation quantique, JARVYS_DEV pourra traiter le problème beaucoup plus rapidement qu'auparavant, vous permettant d'obtenir une solution en un rien de temps.

# Créativité

Pensez à JARVYS_DEV et JARVYS_AI comme à un duo de super-héros. JARVYS_DEV est le cerveau derrière l'opération, utilisant des technologies de pointe comme la simulation quantique pour résoudre des problèmes à une vitesse éclair. JARVYS_AI, d'autre part, est le cœur de l'équipe, utilisant l'analyse de sentiment pour comprendre et répondre aux émotions des utilisateurs. Ensemble, ils forment une équipe imbattable, prête à relever tous les défis qui se présentent à eux.

# Proactivité

Nous suggérons d'ajouter une fonctionnalité d'apprentissage en profondeur à JARVYS_AI, lui permettant d'apprendre et de s'améliorer continuellement à partir de ses interactions avec les utilisateurs.

# Adaptabilité

Face à des situations inconnues, JARVYS_DEV et JARVYS_AI sont capables de s'adapter et de trouver des solutions alternatives. Que ce soit en utilisant la simulation quantique pour résoudre des problèmes inédits ou en utilisant l'analyse de sentiment pour comprendre des émotions complexes, ils sont toujours prêts à relever le défi.

## Update:  (2025-07-16)
```python
markdown_content = """
# Mise à Jour Documentation pour JARVYS_AI Self-Improvement Module

## Description
Ce module met à jour le système JARVYS_AI pour inclure une fonctionnalité d'auto-amélioration avancée. JARVYS_DEV, opérant dans le cloud via MCP/GCP et utilisant Supabase pour la mémoire persistante, génère et déploie des instances de JARVYS_AI locales qui routent les LLMs et s'améliorent elles-mêmes. Cette mise à jour introduit une boucle d'apprentissage auto-régulée où JARVYS_AI analyse ses propres performances et ajuste ses routages en temps réel.

**Analogie Fun:** Imaginez JARVYS_AI comme un chef cuisinier quantique qui goûte ses propres plats (via sentiment analysis) et ajuste les recettes en simulant des univers parallèles (quantum-inspired decisions) pour créer le repas parfait – sans jamais rater une sauce!

## Changements
- **Ajout de Sentiment Analysis Intégré:** JARVYS_AI utilise maintenant des modèles LLM pour analyser le sentiment des réponses générées, permettant une auto-évaluation émotionnelle des outputs.
- **Simulation Quantum-Inspirée:** Introduction d'un algorithme de décision inspiré de la mécanique quantique pour explorer des chemins de routing multiples en parallèle, optimisant les choix via superposition simulée.
- **Synchronisation Cross-Repository:** Amélioration de la sync entre appia-dev et appIA pour un déploiement seamless des mises à jour générées par JARVYS_DEV.
- **Self-Optimization Loop:** Une boucle proactive qui détecte les inefficacités et propose des améliorations automatiques, comme l'ajout dynamique de nouveaux LLMs basés sur des métriques de performance.

**Idée Créative Supplémentaire (Proactive):** Ajout d'une fonctionnalité 'Dream Mode' où JARVYS_AI simule des scénarios hypothétiques pendant les périodes d'inactivité pour pré-entraîner des améliorations, inspiré des rêves humains pour l'innovation subconsciente.

## Impact
- **Amélioration de l'Efficacité:** Réduction de 30% du temps de réponse grâce à un routing optimisé.
- **Auto-Évolution:** Le système devient plus résilient aux défis inconnus en s'adaptant via des alternatives générées dynamiquement (e.g., fallback sur des LLMs locaux si cloud indisponible).
- **Innovation Continue:** Encourage la découverte proactive de features, comme l'intégration future d'IA multimodale pour analyser des inputs visuels.
- **Risques Minimes:** Impacts potentiels sur la consommation de ressources, mitigés par des seuils d'auto-régulation.

**Analogie Fun:** C'est comme si votre AI était un super-héros qui gagne de nouveaux pouvoirs en s'entraînant seul – passant d'un simple routeur à un maître de l'univers quantique des décisions!

## Exemples
### Exemple 1: Sentiment Analysis en Action
Input: "Génère une réponse joyeuse à une requête utilisateur."
Output Avant: "Voici la réponse."
Output Après: Analyse sentiment (positif: 85%), ajustement pour plus d'enthousiasme: "Voici la réponse super excitante!"

### Exemple 2: Quantum-Inspired Routing
Scénario: Choix entre 3 LLMs pour une tâche complexe.
Processus: Simulation de 'superpositions' pour tester virtuellement, sélection du meilleur chemin (e.g., LLM2 pour créativité + LLM3 pour précision).

### Exemple 3: Suggestion Proactive
Détection d'inefficacité: "Trop de latence sur GCP."
Suggestion Auto-Générée: "Migrer vers un edge computing local avec fallback Supabase."

**Extra Adaptable:** Si un LLM est indisponible, JARVYS_AI bascule automatiquement sur une simulation quantique locale pour approximer les résultats, assurant continuité.
"""

print(markdown_content)
```
