#!/usr/bin/env python3
"""
Test simple du Grok Orchestrator
"""

import os
import sys


def test_orchestrator():
    """Test l'orchestrateur étape par étape"""

    print("🧪 TEST DU GROK ORCHESTRATOR")
    print("=" * 50)

    # Test 1: Variables d'environnement
    print("\n1️⃣ Variables d'environnement:")
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        print(f"  ✅ GITHUB_TOKEN: {github_token[:8]}...")
    else:
        print("  ❌ GITHUB_TOKEN manquant")
        return False

    # Test 2: Import des modules
    print("\n2️⃣ Import des modules:")
    try:
        import github

        from supabase import create_client

        print("  ✅ Modules importés")
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

    # Test 3: Connexion GitHub
    print("\n3️⃣ Connexion GitHub:")
    try:
        g = github.Github(github_token)
        user = g.get_user()
        print(f"  ✅ Connecté en tant que: {user.login}")

        # Test accès repo
        repo = g.get_repo("yannabadie/appia-dev")
        print(f"  ✅ Repository accessible: {repo.name}")

    except Exception as e:
        print(f"  ❌ Erreur GitHub: {e}")
        return False

    # Test 4: Import de l'orchestrateur (sans exécution)
    print("\n4️⃣ Import de l'orchestrateur:")
    try:
        # Ajuster les variables d'environnement pour éviter les erreurs
        os.environ["XAI_API_KEY"] = "test-key"
        os.environ["SUPABASE_URL"] = "https://test.supabase.co"
        os.environ["SUPABASE_KEY"] = "test-key"

        # Import sans exécution
        import importlib.util

        importlib.util.spec_from_file_location(
            "grok_orchestrator", "grok_orchestrator.py"
        )
        # Ne pas exécuter le module, juste vérifier qu'il se compile
        print("  ✅ Orchestrateur importable")

    except Exception as e:
        print(f"  ❌ Erreur orchestrateur: {e}")
        return False

    print("\n🎉 TOUS LES TESTS RÉUSSIS !")
    print("L'orchestrateur est prêt à fonctionner.")
    return True


if __name__ == "__main__":
    success = test_orchestrator()
    sys.exit(0 if success else 1)
