# Configuration JARVYS_AI (Local/Hybride)

Ceci est un placeholder pour le futur agent JARVYS_AI qui s'exécutera en local/hybride et communiquera avec JARVYS_DEV cloud.

## Architecture Prévue

```
┌─────────────────┐         ┌──────────────────┐
│   JARVYS_AI     │◄────────► │   JARVYS_DEV     │
│   (Local/Hybrid)│         │   (Cloud Only)   │
├─────────────────┤         ├──────────────────┤
│ • IDE Integration│         │ • GitHub Actions │
│ • CLI Interface │         │ • Autonomous Loop│
│ • Local Dev     │         │ • Cloud Tasks    │
│ • Code Analysis │         │ • Issue Creation │
└─────────────────┘         └──────────────────┘
          │                            │
          └────────────────────────────┘
                     │
              ┌─────────────┐
              │  Supabase   │
              │   Shared    │
              │ Memory DB   │
              └─────────────┘
```

## Communication Protocol

### JARVYS_AI → JARVYS_DEV
- **Méthode**: GitHub Issues avec label `from_jarvys_ai`
- **Format**: JSON dans le body de l'issue
- **Déclenchement**: Automatic workflow trigger sur JARVYS_DEV

### JARVYS_DEV → JARVYS_AI  
- **Méthode**: GitHub Issues avec label `from_jarvys_dev`
- **Format**: Structured response avec actions/recommendations
- **Traitement**: Local processing par JARVYS_AI

## Mémoire Partagée

### Supabase Tables
- `jarvys_memory`: Mémoire vectorielle infinie
- `jarvys_metrics`: Métriques partagées
- `jarvys_agents_status`: État des agents

### Synchronisation
- **Real-time**: OpenAI embeddings pour recherche sémantique
- **Bidirectional**: Les deux agents enrichissent la mémoire
- **Persistent**: Historique complet des interactions

## Interface Locale JARVYS_AI (À Développer)

```bash
# Installation future
pip install jarvys-ai-cli

# Commandes prévues
jarvys-ai init                    # Configuration initiale
jarvys-ai ask "question"          # Interaction directe
jarvys-ai analyze project        # Analyse de code
jarvys-ai sync                   # Synchronisation mémoire
jarvys-ai status                 # État des agents
jarvys-ai connect jarvys-dev     # Communication cloud
```

## Variables d'Environnement JARVYS_AI

```bash
export JARVYS_AI_MODE="local"
export JARVYS_DEV_REPO="username/appia-dev"  
export GITHUB_TOKEN="ghp_xxx"
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="xxx"
export OPENAI_API_KEY="sk-xxx"
```

## Développement Priority

1. **CLI Interface**: Command-line interface basique
2. **Memory Client**: Accès à la mémoire Supabase
3. **GitHub Integration**: Communication avec JARVYS_DEV
4. **IDE Extensions**: VS Code, JetBrains plugins
5. **Desktop App**: Interface graphique (optionnel)

---

**Note**: JARVYS_AI n'existe pas encore. Ce fichier sert de spécification pour le développement futur de l'agent local/hybride qui complétera l'écosystème JARVYS.
