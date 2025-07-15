#!/usr/bin/env python3
"""
Script de validation finale pour le déploiement JARVYS Dashboard
Vérifie la cohérence de tous les composants et la configuration
"""

from pathlib import Path


class JarvysValidator:
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

    def check_supabase_config(self):
        """Vérifie la configuration Supabase."""
        config_path = "supabase/config.toml"
        if not self.check_file_exists(config_path, "Configuration Supabase"):
            return False

        # Vérifier l'Edge Function
        edge_function_path = "supabase/functions/jarvys-dashboard/index.ts"
        if not self.check_file_exists(edge_function_path, "Edge Function"):
            return False

        with open(edge_function_path, "r") as f:
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
            ("Variable PROJECT_ID", "SUPABASE_PROJECT_ID" in content),
            ("Pas de PROJECT_REF", "SUPABASE_PROJECT_REF" not in content),
            ("Secret SPB_EDGE_FUNCTIONS", "SPB_EDGE_FUNCTIONS" in content),
            ("Health check test", "curl -" in content),
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

    def check_dashboard_files(self):
        """Vérifie les fichiers du dashboard."""
        dashboard_path = "dashboard/main.py"
        if not self.check_file_exists(dashboard_path, "Dashboard FastAPI"):
            return False

        # Vérifier les templates (optionnel)
        templates_path = "dashboard/templates"
        if Path(templates_path).exists():
            self.add_check(
                "Templates dashboard", True, f"Trouvé: {templates_path}", False
            )

        return True

    def check_environment_consistency(self):
        """Vérifie la cohérence des variables d'environnement."""
        devcontainer_path = ".devcontainer/devcontainer.json"
        if not self.check_file_exists(
            devcontainer_path, "DevContainer config"
        ):
            return False

        with open(devcontainer_path, "r") as f:
            content = f.read()

        required_vars = [
            "SUPABASE_SERVICE_ROLE",
            "SUPABASE_PROJECT_ID",
            "SPB_EDGE_FUNCTIONS",
        ]

        for var in required_vars:
            present = var in content
            self.add_check(
                f"DevContainer env - {var}",
                present,
                "Configuré" if present else "Manquant",
                True,
            )

        # Vérifier qu'il n'y a plus de PROJECT_REF
        no_old_ref = "SUPABASE_PROJECT_REF" not in content
        self.add_check(
            "DevContainer - Pas de PROJECT_REF",
            no_old_ref,
            "Nettoyé" if no_old_ref else "Ancien PROJECT_REF encore présent",
            True,
        )

        return True

    def check_dependencies(self):
        """Vérifie les dépendances."""
        # Vérifier pyproject.toml
        pyproject_path = "pyproject.toml"
        if self.check_file_exists(pyproject_path, "PyProject config"):
            with open(pyproject_path, "r") as f:
                content = f.read()

            deps = ["fastapi", "uvicorn", "jinja2", "supabase", "langgraph"]
            for dep in deps:
                present = dep in content
                self.add_check(
                    f"Dépendance - {dep}",
                    present,
                    "Configuré" if present else "Manquant",
                    True,
                )

        # Vérifier requirements.txt
        req_path = "requirements.txt"
        if self.check_file_exists(req_path, "Requirements"):
            with open(req_path, "r") as f:
                content = f.read()

            self.add_check(
                "Requirements - FastAPI",
                "fastapi" in content,
                "Configuré" if "fastapi" in content else "Manquant",
                True,
            )

        return True

    def check_documentation(self):
        """Vérifie la documentation."""
        docs = [
            ("DASHBOARD_CLOUD.md", "Documentation cloud", True),
            ("DEPLOY_QUICK_START.md", "Guide de déploiement", True),
            ("README.md", "Documentation principale", False),
        ]

        for doc_path, description, critical in docs:
            self.check_file_exists(doc_path, description, critical)

        return True

    def run_all_checks(self):
        """Exécute toutes les vérifications."""
        print("🔍 Validation complète de JARVYS Dashboard")
        print("=" * 60)

        # Exécution des vérifications
        self.check_supabase_config()
        self.check_github_workflow()
        self.check_dashboard_files()
        self.check_environment_consistency()
        self.check_dependencies()
        self.check_documentation()

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
        print(
            f"\n📈 Résumé: {len(passed)}/{len(self.checks)} vérifications réussies"
        )

        if critical_failed:
            print(f"\n❌ {len(critical_failed)} erreur(s) critique(s):")
            for error in self.errors:
                print(f"   • {error}")
            print("\n🛠️ Corrigez ces erreurs avant le déploiement!")
            return False

        if self.warnings:
            print(f"\n⚠️ {len(self.warnings)} avertissement(s):")
            for warning in self.warnings:
                print(f"   • {warning}")

        print("\n🎉 Configuration validée et prête pour le déploiement!")
        print("\n📋 Prochaines étapes:")
        print("1. 🔑 Configurez les secrets dans GitHub")
        print("2. 🚀 Pushez sur main pour déclencher le déploiement")
        print("3. 🧪 Testez le dashboard déployé")

        return True


def main():
    """Fonction principale."""
    validator = JarvysValidator()
    success = validator.run_all_checks()

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
