#!/usr/bin/env python3
"""
Script pour configurer l'environnement du Grok Orchestrator avec les variables Codespace
"""

import os


def setup_environment():
    """Configure les variables d'environnement pour l'orchestrateur"""

    # Variables GitHub disponibles dans Codespace
    github_token = os.getenv("GITHUB_TOKEN", os.getenv("SECRET_ACCESS_TOKEN"))
    github_user = os.getenv("GITHUB_USER", "yannabadie")

    # APIs disponibles
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    # Supabase
    supabase_token = os.getenv("SUPABASE_ACCESS_TOKEN")

    # Configuration pour l'orchestrateur
    env_config = {
        "GITHUB_TOKEN": github_token,
        "GH_REPO_DEV": f"{github_user}/appia-dev",
        "GH_REPO_PROD": f"{github_user}/appia-prod",
        "OPENAI_API_KEY": openai_key,
        "GEMINI_API_KEY": gemini_key,
        "SUPABASE_ACCESS_TOKEN": supabase_token,
        "ENVIRONMENT": "dev",
        "CYCLE_DURATION_MINUTES": "60",
        "MAX_CYCLES": "10",
        "LOG_LEVEL": "INFO",
    }

    print("🔧 Configuration de l'environnement Grok Orchestrator:")

    for key, value in env_config.items():
        if value:
            os.environ[key] = value
            # Masquer les tokens dans l'affichage
            display_value = (
                value[:8] + "..."
                if key.endswith("TOKEN") or key.endswith("KEY")
                else value
            )
            print(f"  ✅ {key}: {display_value}")
        else:
            print(f"  ⚠️  {key}: Non disponible")

    return env_config


def test_github_connection():
    """Tester la connexion GitHub"""
    try:
        import github

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("❌ Token GitHub non trouvé")
            return False

        g = github.Github(token)
        user = g.get_user()
        print(f"✅ Connexion GitHub réussie: {user.login}")

        # Tester l'accès au repo
        repo_name = os.getenv("GH_REPO_DEV", "yannabadie/appia-dev")
        repo = g.get_repo(repo_name)
        print(f"✅ Accès au repository: {repo.name}")

        return True

    except Exception as e:
        print(f"❌ Erreur GitHub: {e}")
        return False


def test_apis():
    """Tester les connexions API"""
    results = {}

    # Test OpenAI
    try:
        import openai

        client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
        models = client.models.list()
        print(f"✅ OpenAI: {len(models.data)} modèles disponibles")
        results["openai"] = True
    except Exception as e:
        print(f"❌ OpenAI: {e}")
        results["openai"] = False

    # Test Gemini
    try:
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        print("✅ Gemini: Configuré")
        results["gemini"] = True
    except Exception as e:
        print(f"❌ Gemini: {e}")
        results["gemini"] = False

    return results


if __name__ == "__main__":
    print("🚀 Configuration de l'environnement Grok Orchestrator")
    print("=" * 60)

    # Configuration de base
    env_config = setup_environment()
    print()

    # Test GitHub
    print("🔍 Test de la connexion GitHub:")
    github_ok = test_github_connection()
    print()

    # Test des APIs
    print("🔍 Test des connexions API:")
    api_results = test_apis()
    print()

    # Résumé
    print("📊 RÉSUMÉ DE LA CONFIGURATION:")
    print(f"  GitHub: {'✅' if github_ok else '❌'}")
    print(f"  OpenAI: {'✅' if api_results.get('openai') else '❌'}")
    print(f"  Gemini: {'✅' if api_results.get('gemini') else '❌'}")

    if github_ok and api_results.get("openai"):
        print("\n🎉 Configuration prête pour l'orchestrateur !")
        print("Vous pouvez maintenant exécuter: python grok_orchestrator.py")
    else:
        print("\n⚠️  Configuration incomplète. Vérifiez les erreurs ci-dessus.")
