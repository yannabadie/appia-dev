#!/usr/bin/env python3
"""
Vérification que l'architecture cloud-first est respectée.
Ce script valide que JARVYS_DEV ne peut s'exécuter qu'en cloud.
"""

import os
import sys
from pathlib import Path


def check_cloud_first_architecture():
    """Vérifie que l'architecture cloud-first est respectée."""

    print("🔍 Vérification Architecture Cloud-First JARVYS_DEV")
    print("=" * 60)

    errors = []
    warnings = []

    # 1. Vérifier qu'il n'y a pas de scripts de démarrage local
    local_scripts = [
        "start_jarvys.py",
        "run_local.py",
        "local_server.py",
        "scripts/start.py",
    ]

    for script in local_scripts:
        if Path(script).exists():
            errors.append(f"❌ Script local trouvé: {script}")
        else:
            print(f"✅ Pas de script local: {script}")

    # 2. Vérifier qu'il n'y a pas de dashboard local
    if Path("dashboard").exists():
        errors.append("❌ Dossier dashboard local trouvé")
    else:
        print("✅ Pas de dashboard local")

    # 3. Vérifier qu'il n'y a pas de scripts d'introspection locale
    if Path("scripts").exists():
        errors.append("❌ Dossier scripts local trouvé")
    else:
        print("✅ Pas de scripts d'introspection locale")

    # 4. Vérifier la présence du workflow cloud
    if Path(".github/workflows/jarvys-cloud.yml").exists():
        print("✅ Workflow GitHub Actions cloud présent")
    else:
        errors.append("❌ Workflow cloud manquant")

    # 5. Vérifier la présence du dashboard Supabase
    if Path("supabase/functions/dashboard/index.ts").exists():
        print("✅ Dashboard Supabase Edge Function présent")
    else:
        errors.append("❌ Dashboard Supabase manquant")

    # 6. Vérifier la mémoire infinie
    if Path("src/jarvys_dev/tools/memory_infinite.py").exists():
        print("✅ Mémoire infinie présente")
    else:
        errors.append("❌ Mémoire infinie manquante")

    # 7. Vérifier la configuration des modèles
    if Path("src/jarvys_dev/model_config.json").exists():
        print("✅ Configuration modèles présente")

        # Vérifier le contenu
        import json

        try:
            with open("src/jarvys_dev/model_config.json") as f:
                config = json.load(f)

            expected_models = {
                "openai": "gpt-4o-mini",
                "anthropic": "claude-3-5-sonnet-20241022",
                "gemini": "gemini-1.5-flash",
            }

            for provider, expected_model in expected_models.items():
                if config.get(provider) == expected_model:
                    print(f"✅ Modèle {provider}: {expected_model}")
                else:
                    warnings.append(
                        f"⚠️ Modèle {provider} différent: {config.get(provider)} != {expected_model}"
                    )

        except Exception as e:
            errors.append(f"❌ Erreur lecture config modèles: {e}")
    else:
        errors.append("❌ Configuration modèles manquante")

    # 8. Vérifier les variables d'environnement nécessaires (documentation)
    required_env_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "GITHUB_TOKEN",
    ]

    print("\n🔐 Variables d'environnement requises:")
    for var in required_env_vars:
        if os.getenv(var):
            print(f"✅ {var} définie")
        else:
            warnings.append(f"⚠️ {var} non définie (normale en local)")

    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA VÉRIFICATION")
    print("=" * 60)

    if errors:
        print("❌ ERREURS CRITIQUES:")
        for error in errors:
            print(f"   {error}")
        print("\n🚨 L'architecture cloud-first N'EST PAS respectée!")
        return False

    if warnings:
        print("⚠️ AVERTISSEMENTS:")
        for warning in warnings:
            print(f"   {warning}")

    print("\n✅ Architecture cloud-first VALIDÉE!")
    print("\n🌩️ JARVYS_DEV est configuré pour s'exécuter UNIQUEMENT en cloud")
    print("🏠 JARVYS_AI pourra s'exécuter en local/hybride")
    print("🧠 Mémoire infinie partagée sur Supabase")
    print("📊 Dashboard auto-hébergé sur Supabase Edge Functions")

    return True


def print_deployment_instructions():
    """Affiche les instructions de déploiement."""

    print("\n" + "=" * 60)
    print("🚀 INSTRUCTIONS DE DÉPLOIEMENT")
    print("=" * 60)

    print(
        """
1. 🔧 Configuration Supabase:
   - Créer un projet Supabase
   - Appliquer le schéma: supabase/schema.sql
   - Déployer les fonctions: supabase/functions.sql
   - Déployer le dashboard: supabase functions deploy dashboard

2. 🔐 GitHub Secrets (Repository Settings > Secrets):
   - OPENAI_API_KEY: Clé API OpenAI
   - ANTHROPIC_API_KEY: Clé API Anthropic (optionnel)
   - GEMINI_API_KEY: Clé API Google Gemini (optionnel)
   - SUPABASE_URL: URL de votre projet Supabase
   - SUPABASE_KEY: Service Role Key Supabase
   - SUPABASE_ACCESS_TOKEN: Token d'accès Supabase CLI
   - SUPABASE_PROJECT_ID: ID de votre projet Supabase

3. 🤖 Activation JARVYS_DEV:
   - Push sur main → Déclenche l'exécution automatique
   - Manual trigger → Actions > JARVYS_DEV Cloud Execution
   - Schedule → Toutes les heures automatiquement

4. 📊 Accès Dashboard:
   - URL: https://[votre-projet].supabase.co/functions/v1/dashboard
   - Surveillance en temps réel des agents
   - Recherche dans la mémoire infinie
   - Métriques et analytics
   
5. 🔄 Communication JARVYS_AI (à venir):
   - JARVYS_AI local communique via GitHub Issues
   - Mémoire partagée via Supabase
   - Synchronisation bidirectionnelle
"""
    )


if __name__ == "__main__":
    success = check_cloud_first_architecture()

    if success:
        print_deployment_instructions()
        sys.exit(0)
    else:
        sys.exit(1)
