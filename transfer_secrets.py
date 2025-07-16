from typing import Dict, List, Any, Optional
import json
#!/usr/bin/env python3
"""
🔑 Script de transfert des secrets JARVYS_DEV vers JARVYS_AI (repo appIA)
Exporte l'intégralité des secrets présents chez JARVYS_DEV dans JARVYS_AI
"""

import os
import subprocess
import sys


class SecretsTransfer:
    def __init__(self):
        self.source_repo = "yannabadie/appia-dev"
        self.target_repo = "yannabadie/appIA"
        self.secrets_to_transfer = [
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "SUPABASE_SERVICE_ROLE",
            "SUPABASE_PROJECT_ID",
            "GEMINI_API_KEY",
            "GCP_SA_JSON",
            "GH_TOKEN",
            "GH_REPO",
            "SECRET_ACCESS_TOKEN",
        ]

    def check_gh_auth(self):
        """Vérifier l'authentification GitHub CLI"""
        try:
            _result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True
            )
            if _result.returncode == 0:
                print("✅ GitHub CLI authentifié")
                return True
            else:
                print("❌ GitHub CLI non authentifié")
                print("Exécutez: gh auth login")
                return False
        except FileNotFoundError:
            print("❌ GitHub CLI non installé")
            return False

    def get_secret_value(self, secret_name: str) -> str:
        """Récupérer la valeur d'un secret depuis les variables "
        "d'environnement GitHub Actions"""
        # En mode GitHub Actions, les secrets sont disponibles via
        # l'environnement
        value = os.environ.get(secret_name)
        if value:
            return value
        else:
            print(f"⚠️ Secret {secret_name} non trouvé dans l'environnement")
            return ""

    def set_secret_in_target_repo(
        self,
        secret_name: str,
        secret_value: str,
    ) -> bool:
        """Définir un secret dans le repo cible"""
        try:
            if not secret_value:
                print(f"⚠️ Valeur vide pour {secret_name}, skip")
                return False

            cmd = [
                "gh",
                "secret",
                "set",
                secret_name,
                "-R",
                self.target_repo,
                "-b",
                secret_value,
            ]

            _result = subprocess.run(cmd, capture_output=True, text=True)

            if _result.returncode == 0:
                print(
                    f"✅ Secret {secret_name} transféré vers {self.target_repo}"
                )  # noqa: E501
                return True
            else:
                print(f"❌ Erreur transfert {secret_name}: {_result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Exception lors du transfert {secret_name}: {e}")
            return False

    def transfer_all_secrets(self):
        """Transférer tous les secrets"""
        print(f"🔑 Début du transfert des secrets vers {self.target_repo}")

        success_count = 0
        total_count = len(self.secrets_to_transfer)

        for secret_name in self.secrets_to_transfer:
            print(f"\n📤 Transfert de {secret_name}...")

            # Récupérer la valeur du secret
            secret_value = self.get_secret_value(secret_name)

            if secret_value:
                # Transférer vers le repo cible
                if self.set_secret_in_target_repo(secret_name, secret_value):
                    success_count += 1
            else:
                print(
                    f"⚠️ Secret {secret_name} non disponible, création d'un "
                    "placeholder"
                )
                # Créer un placeholder pour les secrets manquants
                ph = f"PLACEHOLDER_FOR_{secret_name}_UPDATE_WITH_REAL_VALUE"
                placeholder = ph
                if self.set_secret_in_target_repo(secret_name, placeholder):
                    success_count += 1

        print(
            f"\n📊 Résultat: {success_count}/{total_count} secrets transférés"
        )  # noqa: E501

        if success_count == total_count:
            print("✅ Tous les secrets ont été transférés avec succès!")
            return True
        else:
            print("⚠️ Certains secrets n'ont pas pu être transférés")
            return False

    def verify_secrets_in_target(self):
        """Vérifier que les secrets ont bien été créés dans le repo cible"""
        try:
            cmd = ["gh", "secret", "list", "-R", self.target_repo]
            _result = subprocess.run(cmd, capture_output=True, text=True)

            if _result.returncode == 0:
                print(f"\n📋 Secrets dans {self.target_repo}:")
                print(_result.stdout)
                return True
            else:
                print(f"❌ Erreur lors de la vérification: {_result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Exception lors de la vérification: {e}")
            return False


def main():
    """Fonction principale"""
    print("🔑 JARVYS_AI Secrets Transfer Tool")
    print("=" * 50)

    transfer = SecretsTransfer()

    # Vérifier l'authentification
    if not transfer.check_gh_auth():
        sys.exit(1)

    # Transférer les secrets
    if transfer.transfer_all_secrets():
        print("\n🎉 Transfert des secrets terminé avec succès!")

        # Vérifier les secrets dans le repo cible
        transfer.verify_secrets_in_target()

        print(
            f"\n🔗 Repo JARVYS_AI: https://github.com/{transfer.target_repo}"
        )  # noqa: E501
        print(
            "📝 Les secrets sont maintenant disponibles pour les GitHub Actions"
        )  # noqa: E501
    else:
        print("\n❌ Le transfert des secrets a échoué")
        sys.exit(1)


if __name__ == "__main__":
    main()
