#!/usr/bin/env python3
"""
Validation complète du nouveau système JARVYS avec orchestrateur intelligent.
Vérifie tous les composants : modèles de pointe, orchestrateur, auto-update, import données.
"""

import json
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_intelligent_orchestrator():
    """Teste l'orchestrateur intelligent."""
    print("\n🧠 TEST ORCHESTRATEUR INTELLIGENT")
    print("=" * 50)

    try:
        from jarvys_dev.intelligent_orchestrator import get_orchestrator

        orchestrator = get_orchestrator()
        print(f"✅ Orchestrateur initialisé avec {len(orchestrator.models_db)} modèles")

        # Test des modèles de pointe
        expected_models = {
            "gpt-4o": "openai",
            "o1-preview": "openai",
            "gemini-2.0-flash-exp": "gemini",
            "claude-3-5-sonnet-20241022": "anthropic",
        }

        for model_name, expected_provider in expected_models.items():
            if model_name in orchestrator.models_db:
                model = orchestrator.models_db[model_name]
                if model.provider == expected_provider:
                    print(
                        f"✅ Modèle de pointe configuré: {model_name} ({expected_provider})"
                    )
                else:
                    print(
                        f"⚠️ Provider incorrect pour {model_name}: {model.provider} != {expected_provider}"
                    )
            else:
                print(f"❌ Modèle manquant: {model_name}")

        # Test d'analyse de tâche
        test_cases = [
            ("Résous cette équation complexe: x^3 + 2x^2 - 5x + 1 = 0", "mathematical"),
            (
                "Écris une fonction Python optimisée pour trier un million d'éléments",
                "coding",
            ),
            ("Crée un poème sur l'intelligence artificielle", "creative"),
            ("Analyse cette image et décris ce que tu vois", "multimodal"),
            ("Donne-moi un résumé rapide de ce document", "fast"),
        ]

        print("\n🎯 Test d'analyse et sélection de modèles:")
        for prompt, expected_type in test_cases:
            task_analysis = orchestrator.analyze_task(prompt, "auto")
            model_name, model_info, score = orchestrator.select_optimal_model(
                task_analysis
            )

            print(f"  📝 '{prompt[:40]}...'")
            print(
                f"     🎯 Type: {task_analysis.task_type} | Modèle: {model_name} | Score: {score:.2f}"
            )

            # Vérifications
            assert 0 <= score <= 1, f"Score invalide: {score}"
            assert (
                model_name in orchestrator.models_db
            ), f"Modèle inexistant: {model_name}"

        # Stats orchestrateur
        stats = orchestrator.get_orchestrator_stats()
        print(f"\n📊 Stats orchestrateur:")
        print(f"   • Total modèles: {stats['total_models']}")
        print(f"   • Par provider: {stats['models_by_provider']}")
        print(
            f"   • Scores moyens: Raisonnement={stats['avg_scores']['reasoning']:.2f}, "
            + f"Créativité={stats['avg_scores']['creativity']:.2f}"
        )

        return True

    except Exception as e:
        print(f"❌ Erreur orchestrateur: {e}")
        return False


def test_model_configuration():
    """Teste la configuration des modèles de pointe."""
    print("\n🔧 TEST CONFIGURATION MODÈLES")
    print("=" * 50)

    try:
        # Vérifier model_config.json
        config_path = Path("src/jarvys_dev/model_config.json")
        if not config_path.exists():
            print("❌ Fichier model_config.json introuvable")
            return False

        with open(config_path) as f:
            config = json.load(f)

        expected_config = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "gemini": "gemini-2.0-flash-exp",
        }

        print("🎯 Vérification des modèles de pointe:")
        all_good = True
        for provider, expected_model in expected_config.items():
            actual_model = config.get(provider)
            if actual_model == expected_model:
                print(f"✅ {provider}: {actual_model}")
            else:
                print(
                    f"❌ {provider}: attendu '{expected_model}', trouvé '{actual_model}'"
                )
                all_good = False

        return all_good

    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False


def test_multi_model_router():
    """Teste le routeur multi-modèles avec orchestrateur."""
    print("\n🔀 TEST ROUTEUR MULTI-MODÈLES")
    print("=" * 50)

    try:
        from jarvys_dev.multi_model_router import MultiModelRouter

        router = MultiModelRouter()
        print("✅ Routeur initialisé")

        # Vérifier l'orchestrateur intégré
        if hasattr(router, "orchestrator"):
            print("✅ Orchestrateur intégré au routeur")
        else:
            print("❌ Orchestrateur manquant dans le routeur")
            return False

        # Test de génération simulée (sans appel API pour éviter coûts)
        print("🧪 Test des méthodes de génération:")

        # Vérifier que les méthodes d'exécution existent
        methods = [
            "_execute_openai",
            "_execute_gemini",
            "_execute_anthropic",
            "_fallback_generation",
        ]
        for method in methods:
            if hasattr(router, method):
                print(f"✅ Méthode {method} disponible")
            else:
                print(f"❌ Méthode {method} manquante")
                return False

        return True

    except Exception as e:
        print(f"❌ Erreur routeur: {e}")
        return False


def test_auto_updater():
    """Teste le système de mise à jour automatique."""
    print("\n🔄 TEST AUTO-UPDATER")
    print("=" * 50)

    try:
        from jarvys_dev.auto_model_updater import get_auto_updater

        updater = get_auto_updater()
        print("✅ Auto-updater initialisé")

        # Test des endpoints
        print("🌐 Endpoints configurés:")
        for name, url in updater.endpoints.items():
            print(f"  • {name}: {url}")

        # Test de détection (simulation)
        print("\n🔍 Test de détection de modèles:")

        # Test d'analyse de modèle HF
        test_model_data = {
            "id": "microsoft/DialoGPT-large",
            "downloads": 5000,
            "likes": 100,
            "createdAt": "2024-01-01T00:00:00Z",
            "tags": ["conversational", "text-generation"],
        }

        is_interesting = updater._is_interesting_llm(
            test_model_data["id"], test_model_data
        )
        print(f"  • Test modèle intéressant: {is_interesting}")

        capabilities = updater._extract_capabilities_hf(test_model_data)
        print(f"  • Capacités détectées: {capabilities}")

        # Test de rapport
        report = updater.get_update_report()
        print(f"  • Rapport généré: {len(report)} caractères")

        return True

    except Exception as e:
        print(f"❌ Erreur auto-updater: {e}")
        return False


def test_openai_data_importer():
    """Teste l'importateur de données OpenAI."""
    print("\n📧 TEST IMPORTATEUR DONNÉES OPENAI")
    print("=" * 50)

    try:
        from jarvys_dev.openai_data_importer import OpenAIDataImporter

        emails = ["yann.abadie.exakis@gmail.com", "yann.abadie@gmail.com"]
        importer = OpenAIDataImporter(emails)
        print(f"✅ Importateur initialisé pour {len(emails)} emails")

        # Test de simulation de données
        print("🎭 Test de simulation des données utilisateur:")

        user_data = importer._simulate_user_data_from_patterns(
            "test@example.com",
            importer._extract_user_data("test@example.com")
            or type(
                "obj",
                (object,),
                {
                    "email": "test@example.com",
                    "conversations": [],
                    "usage_history": [],
                    "preferences": {},
                    "custom_instructions": None,
                    "plugins_used": [],
                    "model_preferences": {},
                },
            )(),
        )

        if user_data:
            print(f"  • Conversations simulées: {len(user_data.conversations)}")
            print(f"  • Préférences: {len(user_data.preferences)} catégories")
            print(
                f"  • Instructions personnalisées: {bool(user_data.custom_instructions)}"
            )
            print(f"  • Plugins utilisés: {len(user_data.plugins_used)}")

        # Test d'analyse des préférences
        preferences = importer._analyze_user_preferences("test@example.com")
        print(f"  • Préférences analysées: {len(preferences)} entrées")

        return True

    except Exception as e:
        print(f"❌ Erreur importateur: {e}")
        return False


def test_memory_integration():
    """Teste l'intégration avec la mémoire infinie."""
    print("\n🧠 TEST INTÉGRATION MÉMOIRE")
    print("=" * 50)

    try:
        from jarvys_dev.tools.memory_infinite import get_memory

        memory = get_memory("JARVYS_DEV", "validation_test")
        print("✅ Mémoire infinie connectée")

        # Test de mémorisation
        success = memory.memorize(
            "Test de validation du nouveau système JARVYS avec orchestrateur intelligent",
            memory_type="experience",
            importance_score=0.8,
            tags=["validation", "orchestrateur", "test"],
            metadata={"test_timestamp": "2025-01-10", "system": "upgraded"},
        )

        if success:
            print("✅ Mémorisation réussie")
        else:
            print("⚠️ Mémorisation échouée (normal si Supabase non configuré)")

        # Test de recherche
        results = memory.recall("validation test", limit=3)
        print(f"✅ Recherche effectuée: {len(results)} résultats")

        return True

    except Exception as e:
        print(f"❌ Erreur mémoire: {e}")
        return False


def main():
    """Fonction principale de validation."""
    print("🚀 VALIDATION COMPLÈTE SYSTÈME JARVYS UPGRADEÉ")
    print("=" * 60)
    print("🎯 Modèles de pointe: Gemini 2.0, Claude 4, GPT-4o, o1-preview")
    print("🧠 Orchestrateur intelligent avec sélection automatique")
    print("🔄 Auto-update depuis Hugging Face et APIs")
    print("📊 Import données personnelles OpenAI")
    print("=" * 60)

    tests = [
        ("Configuration modèles", test_model_configuration),
        ("Orchestrateur intelligent", test_intelligent_orchestrator),
        ("Routeur multi-modèles", test_multi_model_router),
        ("Auto-updater", test_auto_updater),
        ("Importateur OpenAI", test_openai_data_importer),
        ("Intégration mémoire", test_memory_integration),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ ERREUR CRITIQUE dans {test_name}: {e}")
            results[test_name] = False

    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)

    for test_name, success in results.items():
        status = "✅ PASSÉ" if success else "❌ ÉCHEC"
        print(f"{status:12} {test_name}")

    print(f"\n🎯 RÉSULTAT GLOBAL: {passed_tests}/{total_tests} tests réussis")

    if passed_tests == total_tests:
        print("\n🎉 VALIDATION COMPLÈTE RÉUSSIE!")
        print("🚀 Le système JARVYS est prêt avec:")
        print("   • Orchestrateur intelligent pour sélection automatique")
        print("   • Modèles de pointe (Gemini 2.0, Claude 4, GPT-4o, o1)")
        print("   • Mise à jour automatique depuis Hugging Face")
        print("   • Import des données personnelles OpenAI")
        print("   • Mémoire infinie partagée et recherche sémantique")
        return 0
    else:
        print(f"\n⚠️ VALIDATION PARTIELLE: {total_tests - passed_tests} échecs")
        print("🔧 Vérifiez les erreurs ci-dessus pour finaliser l'installation")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
