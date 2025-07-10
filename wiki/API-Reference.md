# 📚 Référence API JARVYS_DEV

*Générée automatiquement le 10/07/2025 à 18:20*

## 🔧 Modules Principaux

### `jarvys_dev.langgraph_loop`

La boucle principale basée sur LangGraph qui orchestre le comportement autonome.

**Fonctions disponibles:**


```python
from jarvys_dev.langgraph_loop import run_loop

# Exécuter 1 cycle autonome
state = run_loop(steps=1)
print(state)
```

### `jarvys_dev.multi_model_router`

Routeur intelligent pour les modèles LLM avec fallback automatique.

```python
from jarvys_dev.multi_model_router import MultiModelRouter

router = MultiModelRouter()
response = router.generate("Explain this code", task_type="reasoning")
```

**Types de tâches supportés:**
- `reasoning`: Raisonnement logique (OpenAI → Anthropic → Gemini)
- `multimodal`: Traitement multimodal (Gemini → OpenAI → Anthropic)
- `creativity`: Tâches créatives (OpenAI → Anthropic → Gemini)

## 🛠️ Outils (Tools)

### `jarvys_dev.tools.github_tools`
GitHub helpers.

Secrets nécessaires : GH_TOKEN, GH_REPO

**Fonctions disponibles:**

### `jarvys_dev.tools.memory`
No description available

**Fonctions disponibles:**


## 🔄 États de la Boucle

```python
class LoopState(TypedDict):
    observation: str              # Observation actuelle
    plan: str                    # Plan d'action généré
    action_url: str              # URL de l'action effectuée
    reflected: bool              # État de la réflexion
    waiting_for_human_review: bool  # Escalade vers humain
```

## 🎛️ Configuration

### Variables d'environnement

| Variable | Requis | Description |
|----------|--------|-------------|
| `OPENAI_API_KEY` | ✅ | Clé API OpenAI |
| `GH_TOKEN` | ✅ | Token GitHub |
| `GH_REPO` | ✅ | Repository GitHub (owner/repo) |
| `SUPABASE_URL` | ✅ | URL Supabase |
| `SUPABASE_KEY` | ✅ | Clé Supabase |
| `GEMINI_API_KEY` | ✅ | Clé Google AI |
| `GCP_SA_JSON` | ✅ | Service Account GCP (JSON) |
| `ANTHROPIC_API_KEY` | ❌ | Clé Anthropic (optionnel via GitHub Copilot) |
| `CONFIDENCE_SCORE` | ❌ | Score de confiance (défaut: 1.0) |

### Configuration des modèles

Le fichier `src/jarvys_dev/model_config.json` est mis à jour automatiquement par le model watcher :

```json
{
  "openai": "whisper-1",
  "anthropic": "claude-4",
  "gemini": "models/text-embedding-004"
}
```

## 🔌 Intégrations

### Github
- **Fonctionnalités**: Issues, PRs, Projects, GraphQL
- **Secrets requis**: GH_TOKEN, GH_REPO

### Supabase
- **Fonctionnalités**: Vector DB, RLS, SQL functions
- **Secrets requis**: SUPABASE_URL, SUPABASE_KEY


### Serveur MCP
- **Port**: 54321
- **Type**: Model Context Protocol
- **Endpoints**: /v1/tool-metadata, /v1/tool-invocations/ask_llm


## 📊 Monitoring

### Benchmarking automatique
```python
router = MultiModelRouter()
response = router.generate("test")

# Accès aux métriques  
for benchmark in router.benchmarks:
    print("Model:", benchmark.model)
    print("Latency:", benchmark.latency)
    print("Cost proxy:", benchmark.cost)
```

### Logs sécurisés
Les secrets sont automatiquement masqués dans les logs grâce au `_SecretFilter`.

---

*Cette documentation API est générée automatiquement depuis le code source.*
