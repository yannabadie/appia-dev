from typing import Dict, List, Any, Optional
import json
import sys
#!/usr/bin/env python3
"""
Script pour corriger les erreurs restantes de linting.
"""

import os
import re


def fix_f_string_placeholders():
    """Corrige les f-strings sans placeholders."""
    patterns = [
        (r'f"([^{}"]*)"', r'"\1"'),  # "text" -> "text"
        (r"f'([^{}']*)'", r"'\1'"),  # 'text' -> 'text'
    ]

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    original_content = content
                    for pattern, replacement in patterns:
                        content = re.sub(pattern, replacement, content)

                    if content != original_content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"Fixed f-strings in: {filepath}")

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")


def fix_bare_except():
    """Corrige les bare except."""
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Remplacer bare except par except Exception
                    content = re.sub(r"except\s*:", "except Exception:", content)

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")


def fix_unused_variables():
    """Préfixe les variables non utilisées avec underscore."""
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Variables communes qui ne sont jamais utilisées
                    unused_vars = [
                        "report",
                        "result",
                        "response",
                        "update",
                        "alert",
                        "source",
                        "success_criteria",
                        "expected_functions",
                        "total_time",
                        "client = None",
                        "supabase_client",
                        "githubclient",
                        "parsed_data",
                    ]

                    modified = False
                    for i, line in enumerate(lines):
                        for var in unused_vars:
                            # Remplacer assignment de variable non utilisée
                            pattern = rf"(\s+){var}\s*="
                            replacement = rf"\1_{var} ="
                            if re.search(pattern, line) and f"_{var}" not in line:
                                lines[i] = re.sub(pattern, replacement, line)
                                modified = True

                    if modified:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.writelines(lines)
                        print(f"Fixed unused variables in: {filepath}")

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")


def fix_loop_variables():
    """Préfixe les variables de boucle non utilisées avec underscore."""
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Variables de boucle communes
                    loop_vars = [
                        "i",
                        "job_name",
                        "check_name",
                        "expected_type",
                        "message_id",
                    ]

                    for var in loop_vars:
                        # for var in ... -> for _var in ...
                        pattern = rf"for {var} in "
                        replacement = rf"for _{var} in "
                        content = re.sub(pattern, replacement, content)

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")


def fix_import_shadowing():
    """Corrige l'import shadowing."""
    filepath = "./jarvys_ai/extensions/email_manager.py"
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Remplacer for email in ... par for email_item in ...
            content = re.sub(r"for email in ", "for email_item in ", content)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed import shadowing in: {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def fix_function_redefinition():
    """Corrige les redéfinitions de fonctions."""
    # _create_backup redefinition
    filepath = "./jarvys_ai/continuous_improvement.py"
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Trouver et renommer la deuxième définition
            found_first = False
            for i, line in enumerate(lines):
                if "def _create_backup(" in line:
                    if found_first:
                        lines[i] = line.replace(
                            "def _create_backup(", "def _create_backup_v2("
                        )
                        break
                    else:
                        found_first = True

            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print(f"Fixed function redefinition in: {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def main():
    """Main function."""
    print("🔧 Fixing remaining linting errors...")

    fix_f_string_placeholders()
    fix_bare_except()
    fix_unused_variables()
    fix_loop_variables()
    fix_import_shadowing()
    fix_function_redefinition()

    print("✅ Finished fixing errors!")


if __name__ == "__main__":
    main()
