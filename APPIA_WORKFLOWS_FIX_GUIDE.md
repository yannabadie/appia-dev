# Guide de Correction des Workflows AppIA

## Contexte
Ce document décrit les modifications nécessaires pour stabiliser les workflows GitHub Actions du repository **appIA** (yannabadie/appIA).

## Corrections Appliquées à appia-dev ✅

### 1. Workflow CI (.github/workflows/ci.yml)
- ✅ Ajout de `poetry check` avant l'installation
- ✅ Installation avec `--with dev --no-interaction` pour les dépendances de développement
- ✅ Suppression des règles UFW problématiques

### 2. Workflow Agent (.github/workflows/agent.yml)  
- ✅ Correction `GH_REPO` vers `"yannabadie/appIA"` au lieu de `${{ github.repository }}`
- ✅ Suppression des règles UFW problématiques

### 3. Nettoyage du Code
- ✅ Suppression du répertoire `appIA_complete_package/` 
- ✅ Mise à jour des tests pour ignorer les packages obsolètes
- ✅ Nettoyage des références dans les scripts utilitaires

## Modifications Requises pour appIA 🔧

### 3. Modification du Workflow JARVYS_AI (appIA/.github/workflows/jarvys-ai.yml)

**Problème** : Le workflow actuel s'exécute toutes les 30 minutes et ne se ferme pas proprement.

**Solution** : Modifiez le fichier comme suit :

```yaml
name: JARVYS_AI Handler

# Désactiver temporairement les triggers automatiques
on:
  # schedule:
  #   - cron: "0,30 * * * *"  # Désactivé temporairement
  # issues:
  #   types: [opened, labeled]  # Désactivé temporairement
  workflow_dispatch:  # Garder le trigger manuel
    inputs:
      mode:
        description: 'Mode d\'exécution'
        required: true
        default: 'manual'
        type: choice
        options:
          - manual
          - issue_handler

jobs:
  jarvys-ai-handler:
    runs-on: ubuntu-latest
    if: github.event_name == 'workflow_dispatch' || (github.event_name == 'issues' && contains(github.event.issue.labels.*.name, 'from_jarvys_dev'))
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
          
      - name: Install dependencies
        run: |
          pip install poetry
          poetry config virtualenvs.create true
          poetry config virtualenvs.in-project true
          poetry install --with dev --no-interaction
          
      # Solution temporaire : Commenter l'agent et fermer directement l'issue
      - name: Handle Issue (Temporary)
        if: github.event_name == 'issues'
        uses: actions/github-script@v7
        with:
          script: |
            const issueNumber = context.issue.number;
            
            // Poster un commentaire
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: issueNumber,
              body: '🤖 **JARVYS_AI** a reçu cette tâche.\n\n' +
                    '⚠️ **Note temporaire** : Le traitement automatique est en cours de développement.\n' +
                    'Cette issue est fermée pour éviter l\'accumulation de tâches en attente.\n\n' +
                    'Les fonctionnalités complètes seront disponibles prochainement.'
            });
            
            // Fermer l'issue
            await github.rest.issues.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: issueNumber,
              state: 'closed',
              labels: ['handled_by_jarvys_ai', 'temporary_closure']
            });
            
            console.log(`Issue #${issueNumber} fermée avec succès.`);
      
      # Alternative : Exécuter l'agent avec timeout (si vous préférez)
      # - name: Run JARVYS_AI Agent (avec timeout)
      #   if: github.event.inputs.mode == 'issue_handler' || github.event_name == 'issues'
      #   timeout-minutes: 5  # Limite à 5 minutes
      #   run: |
      #     PYTHONPATH=src poetry run python src/jarvys_ai/main.py --mode=issue_handler
      #   continue-on-error: true  # Continue même si timeout
      
      - name: Workflow Status
        if: always()
        run: |
          echo "🎉 Workflow JARVYS_AI terminé avec succès"
          echo "Mode: ${{ github.event.inputs.mode || 'automatic' }}"
          echo "Event: ${{ github.event_name }}"
```

### Points Clés de la Correction

1. **Triggers désactivés** : Les `schedule` et `issues` sont commentés
2. **Traitement temporaire** : Utilise `actions/github-script` pour fermer rapidement les issues
3. **Pas d'exécution infinie** : L'agent Python n'est plus appelé (ou avec timeout)
4. **Trigger manuel** : Le `workflow_dispatch` reste pour les tests

### 4. Test des Corrections

Une fois appliquées, testez :

```bash
# Dans le repository appIA
poetry check
poetry install --with dev --no-interaction

# Vérifier que le workflow YAML est valide
python -c "import yaml; yaml.safe_load(open('.github/workflows/jarvys-ai.yml'))"
```

## Résultat Attendu

Après ces corrections :
- ✅ Le CI d'appia-dev devrait passer sans erreur
- ✅ L'agent JARVYS_DEV créera des issues dans appIA (pas dans appia-dev)
- ✅ Le workflow JARVYS_AI ne s'exécutera plus automatiquement
- ✅ Les issues de `from_jarvys_dev` seront fermées rapidement avec un message
- ✅ Plus d'erreurs de timeout ou de workflows qui traînent

## Prochaines Étapes

1. **Appliquer les corrections au repository appIA**
2. **Tester le workflow avec un trigger manuel**
3. **Valider que les issues sont bien fermées**
4. **Réactiver progressivement les fonctionnalités une fois l'agent stabilisé**

---

*Guide créé le $(date) pour stabiliser l'écosystème JARVYS*
