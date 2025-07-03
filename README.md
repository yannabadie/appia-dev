# appia-dev

JARVYS_DEV est un agent d'automatisation pour gérer le cycle de vie d'un projet logiciel. Il interagit avec GitHub, une base vectorielle Supabase et des Cloud Functions afin de planifier et exécuter des tâches DevOps.

L'agent s'appuie sur une boucle **observe – plan – act – reflect** mise en œuvre avec LangGraph. Les tâches ainsi planifiées sont transmises à `JARVYS_AI` par création d'issues GitHub étiquetées `from_jarvys_ai`.

Les modifications de code sont générées par Copilot, appliquées sur la branche `dev` puis validées via `pre-commit` et `pytest` avant ouverture de toute PR.

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

Pour les tests locaux, exportez ces variables dans votre shell. Dans GitHub Actions ou Codespaces, définissez-les dans les _Secrets_ du dépôt.

## Exécution des tests

```bash
poetry run pytest -q
```

## Exemple d'exécution

Lancement manuel de la boucle :

```bash
poetry run python -m jarvys_dev.langgraph_loop
```

## Service account key

Le fichier `gcp-sa.json` n'est pas suivi dans le dépôt. Fournissez son contenu via la variable `GCP_SA_JSON`.

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier [`LICENSE`](LICENSE).
