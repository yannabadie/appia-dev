#!/usr/bin/env python3
"""
Test direct et diagnostic de l'API Claude 4 Opus
"""

import asyncio
import os
from datetime import datetime

import anthropic


async def test_claude_api():
    """Test complet de l'API Claude"""

    print("🔍 Diagnostic API Claude 4 Opus")
    print("=" * 50)

    # 1. Vérifier la clé API
    api_key = os.environ.get("CLAUDE_API_KEY", "")

    if not api_key:
        print("❌ CLAUDE_API_KEY non trouvée dans l'environnement")
        return

    print(f"✅ Clé API détectée: {api_key[:15]}...")

    # 2. Vérifier le format de la clé
    if not api_key.startswith("sk-ant-"):
        print("⚠️  La clé API ne commence pas par 'sk-ant-'")
        print("   Vérifiez que vous utilisez une clé valide d'Anthropic")

    # 3. Créer le client
    print("\n📡 Création du client Claude...")

    try:
        # Client synchrone pour test simple
        client = anthropic.Anthropic(api_key=api_key, max_retries=2, timeout=30.0)
        print("✅ Client créé")

        # 4. Test avec différents modèles
        models_to_test = [
            ("claude-opus-4-20250514", "Claude 4 Opus"),
            ("claude-3-opus-20240229", "Claude 3 Opus"),
            ("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet"),
        ]

        for model_id, model_name in models_to_test:
            print(f"\n🧪 Test avec {model_name} ({model_id})...")

            try:
                # Test simple
                response = client.messages.create(
                    model=model_id,
                    max_tokens=50,
                    messages=[{"role": "user", "content": "Réponds juste: OK"}],
                )

                print(f"✅ {model_name} fonctionne!")
                print(f"   Réponse: {response.content[0].text}")
                print(
                    f"   Usage: {response.usage.input_tokens} in, {response.usage.output_tokens} out"
                )

                # Si Claude 4 Opus fonctionne, faire un test plus complet
                if model_id == "claude-opus-4-20250514":
                    print("\n🎯 Test complet Claude 4 Opus...")

                    response = client.messages.create(
                        model=model_id,
                        max_tokens=200,
                        messages=[
                            {
                                "role": "user",
                                "content": "Confirme que tu es Claude 4 Opus et donne 3 de tes capacités principales.",
                            }
                        ],
                    )

                    print("\n💬 Claude 4 Opus répond:")
                    print("-" * 50)
                    print(response.content[0].text)
                    print("-" * 50)

                break  # Si un modèle fonctionne, arrêter

            except anthropic.RateLimitError as e:
                print(f"⚠️  Rate limit atteint: {e}")
                print("   Attendez quelques secondes et réessayez")

            except anthropic.APIStatusError as e:
                print(f"❌ Erreur {e.status_code}: {e.message}")

                if e.status_code == 401:
                    print("   → Clé API invalide ou expirée")
                    print("   → Vérifiez votre clé sur https://console.anthropic.com/")
                elif e.status_code == 403:
                    print("   → Accès refusé - Vérifiez vos permissions")
                    print("   → Votre compte a-t-il accès à ce modèle?")
                elif e.status_code == 404:
                    print(f"   → Modèle {model_id} non trouvé")
                    print(
                        "   → Ce modèle n'est peut-être pas disponible pour votre compte"
                    )
                elif e.status_code == 529:
                    print("   → Serveur surchargé (mais status page OK)")
                    print("   → Peut être un problème de quota ou de région")

            except Exception as e:
                print(f"❌ Erreur inattendue: {type(e).__name__}: {e}")

        # 5. Vérifier les quotas
        print("\n📊 Informations supplémentaires:")
        print("- Date/Heure: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("- Région Codespace: ", os.environ.get("CODESPACE_REGION", "Non définie"))

    except Exception as e:
        print(f"\n❌ Erreur lors de la création du client: {e}")
        print("\nSuggestions:")
        print("1. Vérifiez que votre clé API est valide")
        print("2. Vérifiez que votre compte a accès à Claude 4 Opus")
        print("3. Essayez de régénérer une nouvelle clé API")


async def check_account_info():
    """Vérifier les informations du compte"""
    print("\n\n📋 Vérification du compte Anthropic")
    print("=" * 50)

    api_key = os.environ.get("CLAUDE_API_KEY", "")

    if api_key:
        # Extraire des infos de la clé (sans la révéler)
        key_parts = api_key.split("-")
        if len(key_parts) >= 4:
            print(f"Type de clé: {key_parts[0]}-{key_parts[1]}")
            print(f"ID partiel: ...{key_parts[-1][-4:]}")

    print("\n💡 Pour vérifier votre accès à Claude 4 Opus:")
    print("1. Connectez-vous sur https://console.anthropic.com/")
    print("2. Vérifiez dans 'Plan & Billing' votre niveau d'accès")
    print("3. Claude 4 Opus nécessite peut-être un plan spécifique")
    print("4. Vérifiez aussi vos limites de rate/quota")


# Programme principal
async def main():
    """Menu de diagnostic"""
    print(
        """
    ╔══════════════════════════════════════════════╗
    ║     Diagnostic Claude 4 Opus API             ║
    ╠══════════════════════════════════════════════╣
    ║  1. Test complet de l'API                    ║
    ║  2. Vérifier les infos du compte             ║
    ║  3. Test simple avec curl                    ║
    ║  4. Afficher les variables d'environnement   ║
    ╚══════════════════════════════════════════════╝
    """
    )

    choice = input("Votre choix (1-4): ").strip()

    if choice == "1":
        await test_claude_api()
    elif choice == "2":
        await check_account_info()
    elif choice == "3":
        print("\nCommande curl pour tester:")
        print("```bash")
        print("curl -X POST https://api.anthropic.com/v1/messages \\")
        print('  -H "x-api-key: $CLAUDE_API_KEY" \\')
        print('  -H "anthropic-version: 2023-06-01" \\')
        print('  -H "content-type: application/json" \\')
        print(
            '  -d \'{"model": "claude-opus-4-20250514", "max_tokens": 50, "messages": [{"role": "user", "content": "test"}]}\''
        )
        print("```")
    elif choice == "4":
        print("\nVariables d'environnement pertinentes:")
        for var in [
            "CLAUDE_API_KEY",
            "ANTHROPIC_API_KEY",
            "CODESPACE_NAME",
            "GITHUB_USER",
        ]:
            value = os.environ.get(var, "Non définie")
            if var.endswith("_KEY") and value != "Non définie":
                value = value[:20] + "..."
            print(f"{var}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
