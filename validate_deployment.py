#!/usr/bin/env python3
"""
Script de vérification finale pour le déploiement JARVYS Dashboard
Vérifie que tous les composants sont prêts pour le déploiement sur Supabase
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


class DeploymentValidator:
    def __init__(self):
        self.checks = []
        self.errors = []
        self.warnings = []

    def add_check(
        self, name: str, status: bool, message: str, is_critical: bool = True
    ):
        """Ajoute un résultat de vérification."""
        self.checks.append(
            {
                "name": name,
                "status": status,
                "message": message,
                "critical": is_critical,
            }
        )

        if not status:
            if is_critical:
                self.errors.append(f"{name}: {message}")
            else:
                self.warnings.append(f"{name}: {message}")

    def check_file_exists(
        self, file_path: str, description: str, critical: bool = True
    ):
        """Vérifie l'existence d'un fichier."""
        path = Path(file_path)
        exists = path.exists()
        self.add_check(
            f"Fichier {description}",
            exists,
            f"{'Trouvé' if exists else 'Manquant'}: {file_path}",
            critical,
        )
        return exists

    def check_edge_function(self):
        """Vérifie la fonction Edge Supabase."""
        index_path = "supabase/functions/jarvys-dashboard/index.ts"
        if not self.check_file_exists(index_path, "Edge Function"):
            return False

        # Vérifier le contenu
        with open(index_path, "r") as f:
            content = f.read()

        # Vérifications du contenu
        checks = [
            ("Secret SPB_EDGE_FUNCTIONS", "SPB_EDGE_FUNCTIONS" in content),
            ("Valeur du secret", "dHx8o@3?G4!QT86C" in content),
            ("Fonction serve", "serve(" in content),
            ("Endpoints API", "/api/" in content),
            ("CORS headers", "Access-Control-Allow-Origin" in content),
        ]

        for check_name, condition in checks:
            self.add_check(
                f"Edge Function - {check_name}",
                condition,
                "Configuré" if condition else "Manquant",
                True,
            )

        return all(condition for _, condition in checks)

    def check_github_workflow(self):
        """Vérifie le workflow GitHub Actions."""
        workflow_path = ".github/workflows/deploy-dashboard.yml"
        if not self.check_file_exists(workflow_path, "GitHub Workflow"):
            return False

        with open(workflow_path, "r") as f:
            content = f.read()

        checks = [
            ("Trigger on main", "branches: [ main ]" in content),
            ("Supabase CLI install", "supabase@latest" in content),
            ("Secret configuration", "SPB_EDGE_FUNCTIONS" in content),
            ("Health check test", "curl -f" in content),
            ("Deploy command", "functions deploy" in content),
        ]

        for check_name, condition in checks:
            self.add_check(
                f"GitHub Workflow - {check_name}",
                condition,
                "Configuré" if condition else "Manquant",
                True,
            )

        return all(condition for _, condition in checks)

    def check_deploy_script(self):
        """Vérifie le script de déploiement."""
        script_path = "deploy-supabase.sh"
        if not self.check_file_exists(script_path, "Script de déploiement"):
            return False

        # Vérifier les permissions d'exécution
        path = Path(script_path)
        executable = os.access(path, os.X_OK)
        self.add_check(
            "Script exécutable",
            executable,
            f"{'Exécutable' if executable else 'Permissions manquantes'}",
            False,
        )

        with open(script_path, "r") as f:
            content = f.read()

        checks = [
            ("Shebang bash", content.startswith("#!/bin/bash")),
            ("Vérification Supabase CLI", "supabase" in content),
            ("Déploiement function", "functions deploy" in content),
            ("Configuration secret", "secrets set" in content),
        ]

        for check_name, condition in checks:
            self.add_check(
                f"Deploy Script - {check_name}",
                condition,
                "Configuré" if condition else "Manquant",
                False,
            )

        return True

    def check_supabase_config(self):
        """Vérifie la configuration Supabase."""
        config_path = "supabase/config.toml"
        if not self.check_file_exists(config_path, "Configuration Supabase"):
            return False

        with open(config_path, "r") as f:
            content = f.read()

        # Vérifications basiques
        has_project_id = "project_id" in content
        self.add_check(
            "Configuration Supabase - Project ID",
            has_project_id,
            "Configuré" if has_project_id else "Manquant",
            True,
        )

        return has_project_id

    def check_documentation(self):
        """Vérifie la documentation."""
        docs = [
            ("DASHBOARD_CLOUD.md", "Documentation cloud"),
            ("DEPLOY_QUICK_START.md", "Guide de déploiement rapide"),
            ("README.md", "Documentation principale"),
        ]

        for doc_path, description in docs:
            self.check_file_exists(doc_path, description, False)

    def check_environment_requirements(self):
        """Vérifie les prérequis d'environnement."""
        # Ces vérifications sont informatives
        env_vars = [
            "SUPABASE_ACCESS_TOKEN",
            "SUPABASE_PROJECT_ID",
            "SPB_EDGE_FUNCTIONS",
        ]

        for var in env_vars:
            value = os.getenv(var)
            self.add_check(
                f"Variable d'environnement {var}",
                value is not None,
                f"{'Définie' if value else 'Non définie (configurez dans GitHub/Supabase)'}",
                False,
            )

    def run_all_checks(self):
        """Exécute toutes les vérifications."""
        print("🔍 Vérification de la configuration JARVYS Dashboard")
        print("=" * 60)

        # Exécution des vérifications
        self.check_edge_function()
        self.check_github_workflow()
        self.check_deploy_script()
        self.check_supabase_config()
        self.check_documentation()
        self.check_environment_requirements()

        # Affichage des résultats
        self.print_results()

    def print_results(self):
        """Affiche les résultats des vérifications."""
        print("\n📊 Résultats des Vérifications")
        print("-" * 40)

        # Grouper par statut
        passed = [c for c in self.checks if c["status"]]
        failed = [c for c in self.checks if not c["status"]]
        critical_failed = [c for c in failed if c["critical"]]

        # Affichage des vérifications réussies
        for check in passed:
            print(f"✅ {check['name']}: {check['message']}")

        # Affichage des échecs
        for check in failed:
            icon = "❌" if check["critical"] else "⚠️"
            print(f"{icon} {check['name']}: {check['message']}")

        # Résumé
        print(f"\n📈 Résumé: {len(passed)}/{len(self.checks)} vérifications réussies")

        if critical_failed:
            print(f"\n❌ {len(critical_failed)} erreur(s) critique(s) détectée(s):")
            for error in self.errors:
                print(f"   • {error}")
            print("\n🛠️ Corrigez ces erreurs avant le déploiement!")
            return False

        if self.warnings:
            print(f"\n⚠️ {len(self.warnings)} avertissement(s):")
            for warning in self.warnings:
                print(f"   • {warning}")

        print("\n🎉 Configuration prête pour le déploiement!")
        print("\n📋 Prochaines étapes:")
        print("1. 🔑 Configurez les secrets dans GitHub et Supabase")
        print("2. 🚀 Pushez sur la branche main pour déclencher le déploiement")
        print("3. 🧪 Testez le dashboard avec test_dashboard.py")

        return True


def main():
    """Fonction principale."""
    validator = DeploymentValidator()
    success = validator.run_all_checks()

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
