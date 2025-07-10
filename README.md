# appia-dev

JARVYS_DEV est un agent d'automatisation pour gérer le cycle de vie d'un
projet logiciel. Il interagit avec GitHub, une base vectorielle Supabase et des
Cloud Functions afin de planifier et exécuter des tâches DevOps.

L'agent s'appuie sur une boucle **observe – plan – act – reflect** mise en
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
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GH_TOKEN` et `GH_REPO` pour les fonctions GitHub
   - facultatif : `GCP_SA_JSON` pour les Cloud Functions

Pour les tests locaux, exportez ces variables dans votre shell.
Dans GitHub Actions ou Codespaces, définissez-les dans les _Secrets_ du dépôt.

## Exécution des tests

```bash
poetry run pytest -q
```

## Documentation

La documentation est générée avec [MkDocs](https://www.mkdocs.org/)
et le thème [Material](https://squidfunk.github.io/mkdocs-material/).

### Générer la doc localement

```bash
poetry run mkdocs serve
```

Un workflow _wiki-sync_ publie automatiquement le site sur le Wiki
GitHub lors des pushes sur `main` ou `dev`.

## Example run

Manual loop launch:

```bash
poetry run python -m jarvys_dev.langgraph_loop
```

## Model watcher

The `model_watcher` script checks for new LLM models from OpenAI, Anthropic and
Google Gemini. When a new model is available it updates
`src/jarvys_dev/model_config.json` and opens a GitHub issue.

Run the watcher manually with:

```bash
poetry run python -m jarvys_dev.model_watcher
```

The workflow `model-detection.yml` runs this task daily.
Configure the `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` and
`GH_TOKEN` secrets in your repository settings.

## Service account key

Le fichier `gcp-sa.json` n'est pas suivi dans le dépôt.
Fournissez son contenu via la variable `GCP_SA_JSON`.

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier [`LICENSE`](LICENSE).
