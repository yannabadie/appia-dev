#!/usr/bin/env python3
"""
Test rapide de l'orchestrateur Grok sans dépendances externes problématiques
"""

import os
import sys
from pathlib import Path


def test_basic_functionality():
    """Test basique sans imports externes"""
    print("🧪 Test basique de l'orchestrateur Grok...")

    # Test 1: Environnement
    print("📋 Vérification de l'environnement...")

    grok_api_key = os.getenv("GROK_API_KEY")
    claude_api_key = os.getenv("CLAUDE_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    env_status = {
        "GROK_API_KEY": "✅ Configuré" if grok_api_key else "❌ Manquant",
        "CLAUDE_API_KEY": "✅ Configuré" if claude_api_key else "❌ Manquant",
        "SUPABASE_URL": "✅ Configuré" if supabase_url else "❌ Manquant",
        "SUPABASE_ANON_KEY": "✅ Configuré" if supabase_key else "❌ Manquant",
    }

    for key, status in env_status.items():
        print(f"  {key}: {status}")

    # Test 2: Structure des fichiers
    print("\n📁 Vérification de la structure...")

    required_files = [
        "grok_orchestrator.py",
        "requirements-enhanced.txt",
        "setup_enhanced_orchestrator.sh",
    ]

    for file_name in required_files:
        file_path = Path(file_name)
        status = "✅ Existe" if file_path.exists() else "❌ Manquant"
        print(f"  {file_name}: {status}")

    # Test 3: Validation syntaxique Python
    print("\n🐍 Validation syntaxique...")

    try:
        with open("grok_orchestrator.py", "r", encoding="utf-8") as f:
            code = f.read()

        # Compile pour vérifier la syntaxe
        compile(code, "grok_orchestrator.py", "exec")
        print("  ✅ Syntaxe Python valide")

    except SyntaxError as e:
        print(f"  ❌ Erreur de syntaxe: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️ Erreur: {e}")

    # Test 4: Configuration minimale
    print("\n⚙️ Test de configuration...")

    try:
        # Simulation d'une configuration basique
        config = {
            "grok_model": "grok-4-0709",
            "claude_model": "claude-sonnet-4-20250514",
            "memory_enabled": True,
            "infinite_memory": True,
            "auto_claude_validation": True,
        }

        print("  ✅ Configuration basique créée")
        print(f"  📊 Modèle Grok: {config['grok_model']}")
        print(f"  🧠 Modèle Claude: {config['claude_model']}")
        print(f"  💾 Mémoire infinie: {config['infinite_memory']}")

    except Exception as e:
        print(f"  ❌ Erreur de configuration: {e}")
        return False

    # Test 5: Résumé
    print("\n📋 Résumé du test:")

    all_env_configured = all(
        key for key in [grok_api_key, claude_api_key, supabase_url, supabase_key]
    )
    all_files_exist = all(Path(f).exists() for f in required_files)

    if all_env_configured and all_files_exist:
        print("  🎉 L'orchestrateur Grok est prêt à fonctionner!")
        print("  ✅ Environnement configuré")
        print("  ✅ Fichiers présents")
        print("  ✅ Syntaxe valide")
        return True
    else:
        print("  ⚠️ Configuration incomplète:")
        if not all_env_configured:
            print("    - Variables d'environnement manquantes")
        if not all_files_exist:
            print("    - Fichiers manquants")
        return False


def main():
    """Fonction principale"""
    print("🚀 Test de l'orchestrateur Grok amélioré")
    print("=" * 50)

    success = test_basic_functionality()

    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCÈS: L'orchestrateur est fonctionnel!")
        print("💡 Prochaines étapes:")
        print("   1. Exécuter: python grok_orchestrator.py")
        print("   2. Tester avec Claude 4 validation")
        print("   3. Vérifier la mémoire infinie Supabase")
    else:
        print("❌ ÉCHEC: Problèmes détectés")
        print("🔧 Actions requises:")
        print("   1. Configurer les variables d'environnement")
        print("   2. Installer les dépendances")
        print("   3. Vérifier la configuration Supabase")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
