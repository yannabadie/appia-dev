#!/usr/bin/env python3
"""
Script de correction finale pour les erreurs de syntaxe spécifiques restantes
"""

import os
import re
import subprocess


def fix_logger_assignments(file_path):
    """Corriger les assignations de logger incorrectes"""
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original_content = content

    # Corriger les assignations doubles de logger
    content = re.sub(
        r"logger = logging\.getLogger\(__name__\) = logging\.getLogger\(__name__\)",
        "logger = logging.getLogger(__name__)",
        content,
    )

    # Corriger les appels de logger incorrects
    content = re.sub(
        r"logger = logging\.getLogger\(__name__\)\.(info|error|warning|debug)\(",
        r"logger.\1(",
        content,
    )

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def fix_config_assignments(file_path):
    """Corriger les assignations de config incorrectes"""
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original_content = content

    # Corriger config.get() dans les conditions if
    content = re.sub(r"if (.+?)config\.get\((.+?)\):", r"if \1config.get(\2):", content)
    content = re.sub(
        r"if self\.config\.get\((.+?)\):", r"if self.config.get(\1):", content
    )

    # Corriger config dans les dictionnaires
    content = re.sub(
        r'"(.+?)": config\.get\((.+?)\),', r'"\1": config.get(\2),', content
    )

    # Corriger self.config
    content = re.sub(r"self\.config\)", "self.config)", content)

    # Corriger assert avec config
    content = re.sub(r'assert "(.+?)" in config, ', r'assert "\1" in config, ', content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def fix_function_definitions(file_path):
    """Corriger les définitions de fonction incorrectes"""
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original_content = content

    # Corriger les paramètres par défaut dupliqués
    content = re.sub(r"= None = None\)", "= None)", content)

    # Corriger les paramètres avec config
    content = re.sub(r"\(self\.config\)", "(self.config)", content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def fix_variable_assignments(file_path):
    """Corriger les assignations de variables incorrectes"""
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original_content = content

    # Corriger app
    content = re.sub(r"assert app is not None", "assert app is not None", content)
    content = re.sub(r"app\)", "app)", content)

    # Corriger les variables non définies avec response/result
    content = re.sub(
        r"(\s+)if result\.returncode",
        r"\1result  # Initialize\n\1if result and result.returncode",
        content,
    )
    content = re.sub(
        r"(\s+)print\(result\.", r"\1if result:\n\1    print(result.", content
    )

    # Corriger les chaînes de caractères cassées avec backslash
    content = re.sub(r'f"(.+?)"\\\n\s+for', r'f"\1" for', content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def fix_indentation_errors(file_path):
    """Corriger les erreurs d'indentation"""
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # Cas spécifique pour test_workflows.py
        if "test_workflows.py" in file_path:
            # Reconstruire le fichier proprement
            new_lines = []
            for i, line in enumerate(lines):
                if line.strip().startswith('["poetry"'):
                    # Ajouter la ligne de fonction manquante
                    new_lines.append("def test_generate_wiki_docs():\n")
                    new_lines.append('    """Test génération docs wiki"""\n')
                    new_lines.append('    print("🧪 Test génération wiki docs...")\n')
                    new_lines.append("    try:\n")
                    new_lines.append("        result = subprocess.run(\n")
                    new_lines.append(
                        '            ["poetry", "run", "python", "scripts/generate_wiki_docs.py"],\n'
                    )
                    new_lines.append("            capture_output=True,\n")
                    new_lines.append("            text=True,\n")
                    new_lines.append('            cwd="/workspaces/appia-dev",\n')
                    new_lines.append("        )\n\n")
                    break
                else:
                    new_lines.append(line)

            # Continuer avec le reste du fichier en corrigeant l'indentation
            for j in range(i + 1, len(lines)):
                line = lines[j]
                if line.strip():
                    if (
                        not line.startswith("    ")
                        and not line.startswith("def ")
                        and not line.startswith("class ")
                    ):
                        new_lines.append("        " + line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True

    except Exception as e:
        print(f"Erreur lors de la correction d'indentation de {file_path}: {e}")
        return False

    return False


def main():
    """Fonction principale"""
    print("🔧 Correction finale des erreurs de syntaxe...")

    files_fixed = 0
    error_files = [
        # Erreurs de logger
        "jarvys_ai/continuous_improvement.py",
        "jarvys_ai/dashboard_integration.py",
        "jarvys_ai/digital_twin.py",
        "jarvys_ai/enhanced_fallback_engine.py",
        "jarvys_ai/extensions/email_manager.py",
        "jarvys_ai/extensions/file_manager.py",
        "jarvys_ai/fallback_engine.py",
        "jarvys_ai/intelligence_core.py",
        "jarvys_ai/main.py",
        "scripts/issue_processor.py",
        "src/jarvys_dev/auto_model_updater.py",
        "src/jarvys_dev/intelligent_orchestrator.py",
        "src/jarvys_dev/tools/memory_infinite.py",
        "test_jarvys_ai_complete.py",
        # Erreurs de config et variables
        "tests/test_deployment.py",
        "tests/test_jarvys_dev.py",
        "tools/error_tracker.py",
        "fix_precommit_errors.py",
        "scripts/introspection.py",
        # Erreurs d'indentation
        "test_workflows.py",
    ]

    for file_path in error_files:
        full_path = f"/workspaces/appia-dev/{file_path}"
        fixed = False

        if fix_logger_assignments(full_path):
            fixed = True
        if fix_config_assignments(full_path):
            fixed = True
        if fix_function_definitions(full_path):
            fixed = True
        if fix_variable_assignments(full_path):
            fixed = True
        if fix_indentation_errors(full_path):
            fixed = True

        if fixed:
            files_fixed += 1
            print(f"✅ Corrigé: {file_path}")

    print(f"\n📊 Fichiers corrigés: {files_fixed}")

    # Vérifier le résultat
    result = subprocess.run(
        ["poetry", "run", "ruff", "check", ".", "--statistics"],
        capture_output=True,
        text=True,
        cwd="/workspaces/appia-dev",
    )

    print("\n📈 Statistiques après correction:")
    print(result.stdout)


if __name__ == "__main__":
    main()
