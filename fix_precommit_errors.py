#!/usr/bin/env python3
"""
🔧 Correcteur automatique des erreurs de formatage pre-commit
"""

import re
import subprocess
from pathlib import Path


class PreCommitErrorFixer:
    def __init__(self):
        self.workspace = Path("/workspaces/appia-dev")

    def fix_python_line_length(self, file_path: Path):
        """Corriger les lignes trop longues en Python"""
        print(f"🐍 Correction ligne trop longue: {file_path}")

        content = file_path.read_text()
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if len(line) > 79:
                # Cas spécifique pour les logs
                if "logging.info(" in line and "(" in line and ")" in line:
                    # Diviser la ligne de logging sur plusieurs lignes
                    indent = len(line) - len(line.lstrip())
                    space = " " * indent

                    # Extraire le contenu du logging.info
                    start_idx = line.find("logging.info(")
                    if start_idx != -1:
                        prefix = line[:start_idx]
                        log_content = line[start_idx:]

                        # Diviser le contenu
                        if '"' in log_content:
                            parts = log_content.split('"')
                            if len(parts) >= 3:
                                new_line = f'{prefix}logging.info(\n{space}    "{parts[1]}"\n{space})'
                                lines[i] = new_line

        file_path.write_text("\n".join(lines))
        print(f"✅ Lignes Python corrigées: {file_path}")

    def fix_yaml_formatting(self, file_path: Path):
        """Corriger le formatage YAML"""
        print(f"📄 Correction YAML: {file_path}")

        content = file_path.read_text()
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Corriger les espaces dans les brackets
            if "[" in line and "]" in line:
                # Corriger "[ main ]" -> "[main]"
                line = re.sub(r"\[\s+([^]]+)\s+\]", r"[\1]", line)
                lines[i] = line

            # Supprimer les trailing spaces
            lines[i] = line.rstrip()

            # Corriger l'indentation (cas spécifiques)
            if (
                line.strip().startswith("- ") and "options:" in lines[i - 1]
                if i > 0
                else False
            ):
                # Corriger l'indentation des options de choice
                lines[i] = "          " + line.strip()

        # Reconstruire le contenu
        corrected_content = "\n".join(lines)

        # Corrections spécifiques pour jarvys-cloud.yml
        if "jarvys-cloud.yml" in str(file_path):
            # Corriger l'indentation des options
            corrected_content = corrected_content.replace(
                "options:\n        - autonomous",
                "options:\n          - autonomous",
            )
            corrected_content = corrected_content.replace(
                "        - analysis", "          - analysis"
            )
            corrected_content = corrected_content.replace(
                "        - memory_sync", "          - memory_sync"
            )
            corrected_content = corrected_content.replace(
                "        - dashboard_deploy", "          - dashboard_deploy"
            )

        file_path.write_text(corrected_content)
        print(f"✅ YAML corrigé: {file_path}")

    def fix_markdown_formatting(self, file_path: Path):
        """Corriger le formatage Markdown"""
        print(f"📝 Correction Markdown: {file_path}")

        content = file_path.read_text()
        lines = content.split("\n")

        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Diviser les lignes trop longues
            if len(line) > 80 and line.startswith("JARVYS_AI est un agent"):
                # Diviser cette ligne spécifique
                new_lines.append(
                    "JARVYS_AI est un agent d'intelligence artificielle autonome créé par"
                )
                new_lines.append(
                    "JARVYS_DEV pour l'optimisation continue et l'auto-amélioration du système."
                )
                i += 1
                continue

            # Ajouter des lignes vides autour des headings
            if line.startswith("###") and i > 0 and lines[i - 1].strip() != "":
                new_lines.append("")

            new_lines.append(line)

            # Ajouter ligne vide après les headings
            if (
                line.startswith("###")
                and i < len(lines) - 1
                and lines[i + 1].strip() != ""
            ):
                new_lines.append("")

            # Ajouter lignes vides autour des listes
            if (
                line.startswith("- ")
                and i > 0
                and not lines[i - 1].startswith("- ")
                and lines[i - 1].strip() != ""
            ):
                new_lines.insert(-1, "")

            if (
                i < len(lines) - 1
                and line.startswith("- ")
                and not lines[i + 1].startswith("- ")
                and lines[i + 1].strip() != ""
            ):
                new_lines.append("")

            i += 1

        # Corriger les URLs nues
        content = "\n".join(new_lines)
        content = re.sub(r"(\*\*Dashboard\*\*:\s+)(https://[^\s]+)", r"\1<\2>", content)

        # Ajouter langage aux blocs de code
        content = content.replace("```\n# Installation", "```bash\n# Installation")

        file_path.write_text(content)
        print(f"✅ Markdown corrigé: {file_path}")

    def fix_all_formatting_errors(self):
        """Corriger toutes les erreurs de formatage"""
        print("🔧 Correction automatique des erreurs de formatage")
        print("=" * 55)

        # 1. Corriger verify_and_populate_hybrid.py
        python_file = self.workspace / "verify_and_populate_hybrid.py"
        if python_file.exists():
            self.fix_python_line_length(python_file)

        # 2. Corriger jarvys-cloud.yml
        yaml_file = self.workspace / ".github/workflows/jarvys-cloud.yml"
        if yaml_file.exists():
            self.fix_yaml_formatting(yaml_file)

        # 3. appIA_complete_package removed - moved to separate repository
        # readme_file = self.workspace / "appIA_complete_package/README.md"
        # if readme_file.exists():
        #     self.fix_markdown_formatting(readme_file)

        print("\n✅ Toutes les corrections de formatage appliquées!")

    def run_pre_commit_check(self):
        """Exécuter pre-commit pour valider les corrections"""
        print("🧪 Validation des corrections avec pre-commit...")

        try:
            _result = subprocess.run(
                ["pre-commit", "run", "--all-files"],
                capture_output=True,
                text=True,
                cwd=self.workspace,
            )

            if result.returncode == 0:
                print("✅ Pre-commit validation réussie!")
                return True
            else:
                print("⚠️ Pre-commit encore des erreurs:")
                print(result.stdout[-500:])  # Dernières 500 chars
                return False

        except Exception as e:
            print(f"❌ Erreur pre-commit: {e}")
            return False


def main():
    """Fonction principale"""
    fixer = PreCommitErrorFixer()

    # Corriger les erreurs
    fixer.fix_all_formatting_errors()

    # Valider avec pre-commit
    success = fixer.run_pre_commit_check()

    if success:
        print("\n🎉 Toutes les erreurs de formatage sont corrigées!")
        return 0
    else:
        print("\n⚠️ Certaines erreurs persistent, correction manuelle nécessaire")
        return 1


if __name__ == "__main__":
    exit(main())
