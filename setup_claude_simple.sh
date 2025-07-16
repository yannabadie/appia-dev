#!/bin/bash
# setup_claude_simple.sh
# Installation simplifiée de Claude 4 Opus pour JARVYS

echo "🚀 Installation Simple de Claude 4 Opus pour JARVYS"
echo "=================================================="

# 1. INSTALLATION DES DÉPENDANCES
echo -e "\n📦 Installation des dépendances..."
cd /workspaces/appia-dev

# Utiliser poetry qui est déjà installé
poetry add anthropic python-dotenv

# 2. CRÉATION DU FICHIER CLAUDE
echo -e "\n📝 Création de l'agent Claude 4 Opus..."

cat > claude_agent.py << 'EOF'
#!/usr/bin/env python3
"""
Agent Claude 4 Opus pour JARVYS - Version Simple et Efficace
"""
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# IMPORTANT: Le modèle Claude 4 Opus
CLAUDE_4_OPUS_MODEL = "claude-opus-4-20250514"  # Le vrai nom du modèle Claude 4 Opus

class ClaudeOpusJARVYS:
    def __init__(self):
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("❌ CLAUDE_API_KEY manquante dans .env")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.workspace = Path("/workspaces/appia-dev")
    
    async def analyze_and_fix(self, file_path: str = None):
        """Analyser et corriger un fichier ou tout le projet"""
        print(f"\n🤖 Claude 4 Opus - Analyse JARVYS")
        print("=" * 50)
        
        if file_path:
            # Analyser un fichier spécifique
            await self._analyze_file(file_path)
        else:
            # Analyser les fichiers principaux
            important_files = [
                "grok_orchestrator.py",
                "src/jarvys_dev/tools/memory_infinite.py",
                "app/main.py",
                "pyproject.toml"
            ]
            
            for file in important_files:
                if os.path.exists(file):
                    await self._analyze_file(file)
    
    async def _analyze_file(self, file_path: str):
        """Analyser et corriger un fichier spécifique"""
        print(f"\n📄 Analyse de {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Analyse des problèmes
            analysis = await self.client.messages.create(
                model=CLAUDE_4_OPUS_MODEL,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"""En tant qu'expert Python et architecture IA, analyse ce fichier du projet JARVYS (Double Numérique IA).

Fichier: {file_path}

```python
{content[:3000]}  # Limité pour l'exemple
```

Identifie:
1. Les bugs critiques
2. Les problèmes de sécurité
3. Les optimisations possibles
4. Les améliorations d'architecture

Retourne une analyse structurée avec des exemples concrets."""
                }]
            )
            
            print("\n🔍 Analyse:")
            print(analysis.content[0].text)
            
            # 2. Générer les corrections
            if "grok_orchestrator" in file_path or "memory_infinite" in file_path:
                print("\n🛠️ Génération des corrections...")
                
                fix = await self.client.messages.create(
                    model=CLAUDE_4_OPUS_MODEL,
                    max_tokens=4000,
                    messages=[{
                        "role": "user",
                        "content": f"""Génère le code CORRIGÉ et OPTIMISÉ pour ce fichier.

Applique TOUTES les corrections nécessaires:
- Corriger les bugs
- Améliorer la sécurité
- Optimiser les performances
- Respecter les best practices
- Ajouter la gestion d'erreurs

Code original:
```python
{content}
```

Retourne UNIQUEMENT le code Python corrigé complet."""
                    }]
                )
                
                # Sauvegarder le code corrigé
                fixed_code = fix.content[0].text
                if "```python" in fixed_code:
                    fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
                
                output_file = f"{file_path}.claude_fixed"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                
                print(f"✅ Corrections sauvegardées dans: {output_file}")
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    async def quick_fix_current_error(self, error_message: str, file_path: str = None):
        """Corriger rapidement une erreur spécifique"""
        print(f"\n🚨 Correction rapide de l'erreur...")
        
        context = ""
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                context = f.read()
        
        response = await self.client.messages.create(
            model=CLAUDE_4_OPUS_MODEL,
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Erreur dans JARVYS:
{error_message}

{"Code concerné:" + context[:1000] if context else ""}

Propose une solution CONCRÈTE et le code corrigé."""
            }]
        )
        
        print("\n💡 Solution:")
        print(response.content[0].text)
    
    async def optimize_jarvys_architecture(self):
        """Optimiser l'architecture globale de JARVYS"""
        print("\n🏗️ Analyse architecturale JARVYS...")
        
        # Collecter la structure du projet
        py_files = list(Path(".").rglob("*.py"))[:30]
        structure = "\n".join(str(f) for f in py_files if ".venv" not in str(f))
        
        response = await self.client.messages.create(
            model=CLAUDE_4_OPUS_MODEL,
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""Analyse l'architecture du projet JARVYS (Double Numérique IA):

Objectifs:
- Agent JARVYS_DEV: Orchestrateur cloud (GitHub/GCP/MCP)
- Agent JARVYS_AI: Exécutif local (Windows 11)
- Auto-amélioration continue
- Limite $3/jour
- Multi-LLM (Claude/GPT/Gemini/Mistral)

Structure actuelle:
{structure}

Propose:
1. Améliorations architecturales CONCRÈTES
2. Optimisations des coûts avec exemples de code
3. Intégration optimale de Claude 4 Opus
4. Plan d'action priorisé (1 semaine)"""
            }]
        )
        
        # Sauvegarder le rapport
        with open("JARVYS_Architecture_Claude4Opus.md", 'w') as f:
            f.write(f"# Analyse Architecturale JARVYS - Claude 4 Opus\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(response.content[0].text)
        
        print("\n✅ Rapport sauvegardé: JARVYS_Architecture_Claude4Opus.md")


# Fonctions utilitaires simples
async def main():
    """Menu principal"""
    agent = ClaudeOpusJARVYS()
    
    print("""
    ╔════════════════════════════════════════════╗
    ║     Claude 4 Opus pour JARVYS - Menu       ║
    ╠════════════════════════════════════════════╣
    ║  1. Analyser grok_orchestrator.py          ║
    ║  2. Analyser tout le projet                ║
    ║  3. Corriger une erreur spécifique         ║
    ║  4. Optimiser l'architecture JARVYS        ║
    ║  5. Tout faire (analyse complète)          ║
    ╚════════════════════════════════════════════╝
    """)
    
    choice = input("\nVotre choix (1-5): ").strip()
    
    try:
        if choice == "1":
            await agent.analyze_and_fix("grok_orchestrator.py")
        elif choice == "2":
            await agent.analyze_and_fix()
        elif choice == "3":
            error = input("Collez l'erreur ici: ")
            file = input("Fichier concerné (optionnel): ").strip()
            await agent.quick_fix_current_error(error, file if file else None)
        elif choice == "4":
            await agent.optimize_jarvys_architecture()
        elif choice == "5":
            await agent.analyze_and_fix()
            await agent.optimize_jarvys_architecture()
        else:
            print("❌ Choix invalide")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("\nVérifiez que votre CLAUDE_API_KEY est correcte dans .env")


if __name__ == "__main__":
    asyncio.run(main())
EOF

# 3. CRÉATION DU FICHIER .ENV
echo -e "\n🔐 Configuration de l'environnement..."

if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Claude 4 Opus API
CLAUDE_API_KEY=votre_clé_ici

# Autres clés (déjà configurées)
GH_TOKEN=$GH_TOKEN
SUPABASE_URL=https://kzcswopokvknxmxczilu.supabase.co
SUPABASE_SERVICE_ROLE=votre_clé_service_role
EOF
    echo "⚠️  Ajoutez votre clé CLAUDE_API_KEY dans .env"
fi

# 4. CRÉATION DU SCRIPT DE LANCEMENT
cat > claude.sh << 'EOF'
#!/bin/bash
# Lancer Claude 4 Opus pour JARVYS
poetry run python claude_agent.py
EOF
chmod +x claude.sh

# 5. CRÉATION D'UN RACCOURCI MAKEFILE
if [ -f Makefile ]; then
    echo -e "\n# Claude 4 Opus" >> Makefile
    echo "claude:" >> Makefile
    echo -e "\t./claude.sh" >> Makefile
fi

echo -e "\n✅ Installation terminée!"
echo -e "\n📝 ÉTAPES SUIVANTES:"
echo "1. Obtenez votre clé API Claude sur https://console.anthropic.com/"
echo "2. Ajoutez-la dans .env : nano .env"
echo "3. Lancez Claude : ./claude.sh"
echo -e "\n💡 COMMANDES RAPIDES:"
echo "- Lancer Claude: ./claude.sh"
echo "- Avec Make: make claude"
echo "- Direct: poetry run python claude_agent.py"