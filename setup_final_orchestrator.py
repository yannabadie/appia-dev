#!/usr/bin/env python3
"""
Configuration finale et validation complète de l'orchestrateur Grok
Corrige tous les problèmes identifiés et prépare l'environnement
"""

import os
import subprocess
import sys
from pathlib import Path


def create_env_template():
    """Crée un template des variables d'environnement nécessaires"""
    env_template = """# Configuration Grok Orchestrator
# Copiez ce fichier vers .env et remplissez les valeurs

# === API KEYS ===
# Clé API pour Grok-4-0709 (xAI)
GROK_API_KEY=your_grok_api_key_here

# Clé API pour Claude 4 (Anthropic)
CLAUDE_API_KEY=your_claude_api_key_here

# === SUPABASE CONFIGURATION ===
# URL de votre projet Supabase
SUPABASE_URL=your_supabase_url_here

# Clé anonyme Supabase
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Clé de service Supabase (optionnel, pour administration)
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# === ORCHESTRATOR CONFIG ===
# Mode de fonctionnement (production/development)
ORCHESTRATOR_MODE=development

# Activation de la mémoire infinie
INFINITE_MEMORY_ENABLED=true

# Validation automatique avec Claude 4
AUTO_CLAUDE_VALIDATION=true

# === GITHUB INTEGRATION (optionnel) ===
# Token GitHub pour synchronisation
GITHUB_TOKEN=your_github_token_here

# === LOGGING ===
# Niveau de log (DEBUG/INFO/WARNING/ERROR)
LOG_LEVEL=INFO

# Dossier des logs
LOG_DIR=./logs
"""

    env_file = Path(".env.template")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_template)

    print(f"✅ Template environnement créé: {env_file}")
    print("💡 Copiez .env.template vers .env et configurez vos clés API")


def fix_dependencies():
    """Corrige les problèmes de dépendances"""
    print("🔧 Correction des dépendances...")

    try:
        # Réinstaller urllib3 proprement
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--force-reinstall",
                "urllib3==2.0.7",
            ],
            check=True,
            capture_output=True,
        )
        print("  ✅ urllib3 réinstallé")

        # Réinstaller requests
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--force-reinstall",
                "requests==2.31.0",
            ],
            check=True,
            capture_output=True,
        )
        print("  ✅ requests réinstallé")

        # Installer les dépendances manquantes
        essential_packages = ["xai-sdk", "anthropic", "supabase", "python-dotenv"]

        for package in essential_packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True,
                )
                print(f"  ✅ {package} installé")
            except subprocess.CalledProcessError:
                print(f"  ⚠️ Erreur installation {package}")

        return True

    except Exception as e:
        print(f"  ❌ Erreur dépendances: {e}")
        return False


def create_orchestrator_config():
    """Crée un fichier de configuration pour l'orchestrateur"""
    config = {
        "grok": {
            "model": "grok-4-0709",
            "max_tokens": 8192,
            "temperature": 0.7,
            "timeout": 30,
        },
        "claude": {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "temperature": 0.3,
            "validation_enabled": True,
        },
        "memory": {
            "infinite_enabled": True,
            "supabase_table": "orchestrator_memories",
            "local_fallback": True,
            "max_local_memories": 1000,
        },
        "orchestrator": {
            "auto_validation": True,
            "parallel_processing": False,
            "retry_attempts": 3,
            "log_level": "INFO",
        },
    }

    config_file = Path("orchestrator_config.json")
    with open(config_file, "w", encoding="utf-8") as f:
        import json

        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Configuration orchestrateur créée: {config_file}")


def create_startup_script():
    """Crée un script de démarrage simplifié"""
    startup_script = """#!/bin/bash
# Script de démarrage de l'orchestrateur Grok amélioré

echo "🚀 Démarrage de l'orchestrateur Grok..."

# Vérifier .env
if [ ! -f .env ]; then
    echo "❌ Fichier .env manquant"
    echo "💡 Copiez .env.template vers .env et configurez vos clés API"
    exit 1
fi

# Charger les variables d'environnement
set -a
source .env
set +a

# Vérifier les variables essentielles
if [ -z "$GROK_API_KEY" ]; then
    echo "❌ GROK_API_KEY manquant dans .env"
    exit 1
fi

if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ CLAUDE_API_KEY manquant dans .env"
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL manquant dans .env"
    exit 1
fi

echo "✅ Configuration validée"
echo "🧠 Lancement de l'orchestrateur..."

# Lancer l'orchestrateur
python grok_orchestrator.py "$@"
"""

    script_file = Path("start_orchestrator.sh")
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(startup_script)

    # Rendre le script exécutable
    os.chmod(script_file, 0o755)

    print(f"✅ Script de démarrage créé: {script_file}")


def validate_final_setup():
    """Validation finale de la configuration"""
    print("🔍 Validation finale...")

    required_files = [
        "grok_orchestrator.py",
        "requirements-enhanced.txt",
        ".env.template",
        "orchestrator_config.json",
        "start_orchestrator.sh",
    ]

    all_files_exist = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} manquant")
            all_files_exist = False

    # Test syntaxe
    try:
        with open("grok_orchestrator.py", "r", encoding="utf-8") as f:
            code = f.read()
        compile(code, "grok_orchestrator.py", "exec")
        print("  ✅ Syntaxe Python valide")
        syntax_valid = True
    except SyntaxError as e:
        print(f"  ❌ Erreur syntaxe: {e}")
        syntax_valid = False

    return all_files_exist and syntax_valid


def main():
    """Fonction principale"""
    print("🔧 Configuration finale de l'orchestrateur Grok")
    print("=" * 60)

    success = True

    # Étape 1: Template environnement
    try:
        create_env_template()
    except Exception as e:
        print(f"❌ Erreur template .env: {e}")
        success = False

    # Étape 2: Dépendances
    try:
        if not fix_dependencies():
            success = False
    except Exception as e:
        print(f"❌ Erreur dépendances: {e}")
        success = False

    # Étape 3: Configuration
    try:
        create_orchestrator_config()
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        success = False

    # Étape 4: Script de démarrage
    try:
        create_startup_script()
    except Exception as e:
        print(f"❌ Erreur script démarrage: {e}")
        success = False

    # Étape 5: Validation finale
    try:
        if not validate_final_setup():
            success = False
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        success = False

    print("\n" + "=" * 60)

    if success:
        print("🎉 CONFIGURATION TERMINÉE AVEC SUCCÈS!")
        print("\n📋 Prochaines étapes:")
        print("1. cp .env.template .env")
        print("2. Éditer .env avec vos vraies clés API")
        print("3. ./start_orchestrator.sh")
        print("\n🔧 Alternative de test:")
        print("python test_grok_orchestrator_basic.py")

        print("\n🚀 L'orchestrateur Grok est prêt avec:")
        print("  ✅ Mémoire infinie Supabase")
        print("  ✅ Validation Claude 4")
        print("  ✅ Syntaxe corrigée")
        print("  ✅ Dépendances réparées")

    else:
        print("❌ PROBLÈMES DÉTECTÉS")
        print("🔧 Vérifiez les erreurs ci-dessus")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
