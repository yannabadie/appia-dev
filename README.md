# appia-dev

JARVYS_DEV est un agent d'automatisation pour gérer le cycle de vie d'un
projet logiciel. Il interagit avec GitHub, une base vectorielle Supabase et des
Cloud Functions afin de planifier et exécuter des tâches DevOps.

L'agent s'appuie sur une boucle **observe – plan – act – reflect** mise en
œuvre avec LangGraph. Les tâches ainsi planifiées sont transmises à
`JARVYS_AI` par création d'issues GitHub étiquetées `from_jarvys_ai`.

Les modifications de code sont générées par Copilot, appliquées sur la branche
`dev` puis validées via `pre-commit` et `pytest` avant ouverture de toute PR.

## Mise en route

1. **Installer Poetry**

   ```bash
   pip install poetry
   ```

2. **Installer les dépendances**

   ```bash
   poetry install --with dev
   ```

3. **Variables d'environnement requises**
   
   **Core (obligatoires)** :
   - `OPENAI_API_KEY` - Clé API OpenAI
   - `GH_TOKEN` et `GH_REPO` - Token et repository GitHub  
   - `SUPABASE_URL` et `SUPABASE_KEY` - Base vectorielle Supabase
   - `GEMINI_API_KEY` - Clé Google AI (requis pour le router complet)
   - `GCP_SA_JSON` - Service Account GCP (requis pour Cloud Functions)
   
   **Optionnels** :
   - `ANTHROPIC_API_KEY` - Clé Anthropic (optionnel, GitHub Copilot suffit)
   - `CONFIDENCE_SCORE` - Score de confiance (défaut: 1.0)

Pour les tests locaux, exportez ces variables dans votre shell.
Dans GitHub Actions ou Codespaces, définissez-les dans les _Secrets_ du dépôt.

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
