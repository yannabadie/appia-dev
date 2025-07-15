#!/usr/bin/env python3
"""
Générateur automatique de documentation pour le Wiki GitHub.
Ce script analyse le code source et génère une documentation complète
des capacités et du fonctionnement de JARVYS_DEV.
"""

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ajout du chemin src pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class WikiGenerator:
    """Générateur de documentation Wiki automatisé."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.src_path = repo_root / "src" / "jarvys_dev"
        self.wiki_path = repo_root / "wiki"
        self.capabilities = {}
        self.workflows = {}

    def analyze_code_capabilities(self) -> Dict[str, Any]:
        """Analyse le code pour extraire les capacités automatiquement."""
        capabilities = {
            "core_loop": self._analyze_langgraph_loop(),
            "tools": self._analyze_tools(),
            "models": self._analyze_model_support(),
            "automation": self._analyze_automation_features(),
            "integrations": self._analyze_integrations(),
        }
        return capabilities

    def _analyze_langgraph_loop(self) -> Dict[str, Any]:
        """Analyse la boucle LangGraph principale."""
        loop_file = self.src_path / "langgraph_loop.py"
        with open(loop_file) as f:
            content = f.read()

        # Extraire les fonctions de la boucle
        functions = re.findall(r"^def (\w+)\(.*?\):", content, re.MULTILINE)

        return {
            "type": "Observe-Plan-Act-Reflect Loop",
            "implementation": "LangGraph StateGraph",
            "functions": functions,
            "confidence_threshold": 0.85,
            "features": [
                "Autonomous decision making",
                "Human review escalation",
                "State persistence",
                "Multi-model routing",
            ],
        }

    def _analyze_tools(self) -> Dict[str, Any]:
        """Analyse les outils disponibles."""
        tools_dir = self.src_path / "tools"
        tools = {}

        for tool_file in tools_dir.glob("*.py"):
            if tool_file.name.startswith("test_"):
                continue

            with open(tool_file) as f:
                content = f.read()

            # Extraire les fonctions publiques
            functions = re.findall(
                r"^def ([^_]\w*)\(.*?\):", content, re.MULTILINE
            )

            tools[tool_file.stem] = {
                "file": str(tool_file.relative_to(self.repo_root)),
                "functions": functions,
                "description": self._extract_module_docstring(content),
            }

        return tools

    def _analyze_model_support(self) -> Dict[str, Any]:
        """Analyse le support des modèles LLM."""
        config_file = self.src_path / "model_config.json"

        if config_file.exists():
            with open(config_file) as f:
                models = json.load(f)
        else:
            models = {}

        return {
            "supported_providers": [
                "OpenAI",
                "Google Gemini",
                "Anthropic (via GitHub Copilot)",
            ],
            "current_models": models,
            "features": [
                "Automatic model detection",
                "Fallback strategy",
                "Performance benchmarking",
                "Dynamic routing by task type",
            ],
        }

    def _analyze_automation_features(self) -> Dict[str, Any]:
        """Analyse les fonctionnalités d'automatisation."""
        return {
            "github_automation": [
                "Issue creation with labels",
                "Pull request management",
                "Code generation via Copilot",
                "Branch management",
                "Commit automation",
            ],
            "monitoring": [
                "Model availability tracking",
                "Performance benchmarking",
                "Error logging with secret masking",
                "Confidence scoring",
            ],
            "memory_system": [
                "Vector embeddings via Supabase",
                "Semantic search",
                "Experience persistence",
                "Context retrieval",
            ],
        }

    def _analyze_integrations(self) -> Dict[str, Any]:
        """Analyse les intégrations externes."""
        return {
            "github": {
                "api": "PyGithub",
                "features": ["Issues", "PRs", "Projects", "GraphQL"],
                "secrets": ["GH_TOKEN", "GH_REPO"],
            },
            "supabase": {
                "features": ["Vector DB", "RLS", "SQL functions"],
                "secrets": ["SUPABASE_URL", "SUPABASE_KEY"],
            },
            "llm_providers": {
                "openai": "GPT models + embeddings",
                "gemini": "Google AI models",
                "anthropic": "Claude via GitHub Copilot",
            },
            "mcp_server": {
                "type": "Model Context Protocol",
                "port": 54321,
                "endpoints": [
                    "/v1/tool-metadata",
                    "/v1/tool-invocations/ask_llm",
                ],
            },
        }

    def _extract_module_docstring(self, content: str) -> str:
        """Extrait la docstring du module."""
        try:
            tree = ast.parse(content)
            if isinstance(tree.body[0], ast.Expr) and isinstance(
                tree.body[0].value, ast.Constant
            ):
                return tree.body[0].value.value.strip()
        except Exception:
            pass
        return "No description available"

    def _analyze_workflows(self) -> Dict[str, Any]:
        """Analyse les workflows GitHub Actions."""
        workflows_dir = self.repo_root / ".github" / "workflows"
        workflows = {}

        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.yml"):
                workflows[workflow_file.stem] = {
                    "file": str(workflow_file.relative_to(self.repo_root)),
                    "triggers": self._extract_workflow_triggers(workflow_file),
                }

        return workflows

    def _extract_workflow_triggers(self, workflow_file: Path) -> List[str]:
        """Extrait les triggers d'un workflow."""
        with open(workflow_file) as f:
            content = f.read()

        triggers = []
        if "schedule:" in content:
            triggers.append("scheduled")
        if "push:" in content:
            triggers.append("push")
        if "pull_request:" in content:
            triggers.append("pull_request")
        if "workflow_dispatch:" in content:
            triggers.append("manual")

        return triggers

    def generate_home_page(self) -> str:
        """Génère la page d'accueil du Wiki."""
        capabilities = self.analyze_code_capabilities()
        workflows = self._analyze_workflows()

        # Préparer les données pour éviter les f-string complexes
        current_date = self._get_current_date()
        loop_type = capabilities["core_loop"]["type"]
        loop_impl = capabilities["core_loop"]["implementation"]
        confidence_threshold = capabilities["core_loop"][
            "confidence_threshold"
        ]
        providers = self._format_list(
            capabilities["models"]["supported_providers"]
        )
        models_json = json.dumps(
            capabilities["models"]["current_models"], indent=2
        )

        content = """# 🤖 JARVYS_DEV - Agent DevOps Autonome

*Documentation générée automatiquement le {current_date}*

## 🎯 Vue d'ensemble

JARVYS_DEV est un agent d'automatisation DevOps qui implémente une boucle autonome **Observe-Plan-Act-Reflect** pour gérer le cycle de vie d'un projet logiciel. Il combine l'intelligence artificielle avec l'automatisation pour fournir une assistance DevOps intelligente et proactive.

## 🏗️ Architecture Technique

### Boucle Principale
- **Type**: {loop_type}
- **Implémentation**: {loop_impl}
- **Seuil de confiance**: {confidence_threshold}

### Modèles LLM Supportés
{providers}

**Modèles actuels configurés:**
```json
{models_json}
```

## ⚡ Capacités Autonomes

### 🤖 Automatisation GitHub
{self._format_list(capabilities['automation']['github_automation'])}

### 📊 Monitoring & Observabilité
{self._format_list(capabilities['automation']['monitoring'])}

### 🧠 Système de Mémoire
{self._format_list(capabilities['automation']['memory_system'])}

## 🔧 Outils Disponibles

{self._format_tools(capabilities['tools'])}

## 🔄 Workflows Automatisés

{self._format_workflows(workflows)}

## 🌐 Intégrations

### GitHub
- **API**: {capabilities['integrations']['github']['api']}
- **Fonctionnalités**: {', '.join(capabilities['integrations']['github']['features'])}

### Supabase (Base Vectorielle)
- **Fonctionnalités**: {', '.join(capabilities['integrations']['supabase']['features'])}

### Serveur MCP (Model Context Protocol)
- **Port**: {capabilities['integrations']['mcp_server']['port']}
- **Endpoints**: {', '.join(capabilities['integrations']['mcp_server']['endpoints'])}

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
export GCP_SA_JSON='{{"type": "service_account", "project_id": "your_project"}}'
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
"""
        return content

    def generate_api_reference(self) -> str:
        """Génère la référence API complète."""
        capabilities = self.analyze_code_capabilities()

        content = """# 📚 Référence API JARVYS_DEV

*Générée automatiquement le {self._get_current_date()}*

## 🔧 Modules Principaux

### `jarvys_dev.langgraph_loop`

La boucle principale basée sur LangGraph qui orchestre le comportement autonome.

**Fonctions disponibles:**
{self._format_list(capabilities['core_loop']['functions'])}

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

{self._format_tools_api(capabilities['tools'])}

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
{json.dumps(capabilities['models']['current_models'], indent=2)}
```

## 🔌 Intégrations

{self._format_integrations_api(capabilities['integrations'])}

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
"""
        return content

    def _format_list(self, items: List[str]) -> str:
        """Formate une liste en Markdown."""
        return "\n".join(f"- {item}" for item in items)

    def _format_tools(self, tools: Dict[str, Any]) -> str:
        """Formate la liste des outils."""
        formatted = []
        for name, info in tools.items():
            formatted.append(f"### {name}")
            formatted.append(f"- **Fichier**: `{info['file']}`")
            formatted.append(f"- **Description**: {info['description']}")
            if info["functions"]:
                formatted.append(
                    f"- **Fonctions**: {', '.join(info['functions'])}"
                )
            formatted.append("")
        return "\n".join(formatted)

    def _format_tools_api(self, tools: Dict[str, Any]) -> str:
        """Formate la documentation API des outils."""
        formatted = []
        for name, info in tools.items():
            formatted.append(f"### `jarvys_dev.tools.{name}`")
            formatted.append(f"{info['description']}")
            formatted.append("")
            formatted.append("**Fonctions disponibles:**")
            for func in info["functions"]:
                formatted.append(f"- `{func}()`")
            formatted.append("")
        return "\n".join(formatted)

    def _format_workflows(self, workflows: Dict[str, Any]) -> str:
        """Formate la liste des workflows."""
        formatted = []
        for name, info in workflows.items():
            triggers = (
                ", ".join(info["triggers"]) if info["triggers"] else "manual"
            )
            formatted.append(f"- **{name}**: {triggers}")
        return "\n".join(formatted)

    def _format_integrations_api(self, integrations: Dict[str, Any]) -> str:
        """Formate la documentation des intégrations."""
        formatted = []
        for name, info in integrations.items():
            if name == "mcp_server":
                formatted.append("### Serveur MCP")
                formatted.append(f"- **Port**: {info['port']}")
                formatted.append(f"- **Type**: {info['type']}")
                formatted.append(
                    "- **Endpoints**: " + ", ".join(info["endpoints"])
                )
            elif isinstance(info, dict) and "features" in info:
                formatted.append(f"### {name.title()}")
                formatted.append(
                    "- **Fonctionnalités**: " + ", ".join(info["features"])
                )
                if "secrets" in info:
                    formatted.append(
                        "- **Secrets requis**: " + ", ".join(info["secrets"])
                    )
            formatted.append("")
        return "\n".join(formatted)

    def _get_current_date(self) -> str:
        """Retourne la date actuelle."""
        from datetime import datetime

        return datetime.now().strftime("%d/%m/%Y à %H:%M")

    def generate_all_docs(self):
        """Génère toute la documentation Wiki."""
        print("🔍 Analyse du code source...")

        # Créer le dossier wiki s'il n'existe pas
        self.wiki_path.mkdir(exist_ok=True)

        # Générer Home.md
        print("📝 Génération de Home.md...")
        home_content = self.generate_home_page()
        (self.wiki_path / "Home.md").write_text(home_content)

        # Générer API-Reference.md
        print("📚 Génération de API-Reference.md...")
        api_content = self.generate_api_reference()
        (self.wiki_path / "API-Reference.md").write_text(api_content)

        print("✅ Documentation Wiki générée avec succès!")
        print(f"📁 Fichiers créés dans: {self.wiki_path}")


def main():
    """Point d'entrée principal."""
    repo_root = Path(__file__).parent.parent
    generator = WikiGenerator(repo_root)
    generator.generate_all_docs()


if __name__ == "__main__":
    main()
