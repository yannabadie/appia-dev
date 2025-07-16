#!/usr/bin/env python3
"""Script pour corriger les variables mal préfixées dans les tests."""

import os
import re


def fix_variable_prefixes(file_path):
    """Corrige les variables préfixées incorrectement."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Pattern pour trouver des assignations avec _ mais utilisations sans _
    patterns_to_fix = [
        # _client = ... mais utilisé comme client  # To be initialized
        (r"(\s+)_client = ([^\n]+)", r"\1client = \2"),
        (r"(\s+)_response = ([^\n]+)", r"\1_response = \2"),
        # Ensuite corriger les utilisations
        (r"(\s+)_response = client\.", r"\1response = client."),
        (r"assert response\.", r"assert response."),
        (r"if response\.", r"if response."),
        (r"response\.status_code", r"response.status_code"),
        (r"(\s+)_result = ([^\n]+)", r"\1_result = \2"),
        # Puis corriger les utilisations de result
        (r"(\s+)_result = ([^=\n]+\.get[^\n]*)", r"\1result = \2"),
        (r"assert _result", r"assert result"),
        (r"if _result", r"if result"),
        # Patterns spécifiques aux tests
        (r"(\s+)_processor = ([^\n]+)", r"\1processor = \2"),
        (r"processor\.", r"processor."),
    ]

    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content)

    # Fix spécifique pour les erreurs que nous avons vues
    specific_fixes = [
        # Dans test_api_integration.py
        ("_response = client.get", "response = client.get"),
        ("_response = client.post", "response = client.post"),
        ("_response = requests.get", "response = requests.get"),
        ("_response = requests.post", "response = requests.post"),
        ("_client = TestClient", "client = TestClient"),
        ("_client = Github", "client = Github"),
        ("_client = OpenAI", "client = OpenAI"),
        # Variables utilisées mais préfixées
        ("_processor = IssueProcessor", "processor = IssueProcessor"),
        ("_result = subprocess.run", "result = subprocess.run"),
        ("_expected_functions =", "expected_functions ="),
        ("_success_criteria =", "success_criteria ="),
        ("_supabase_client =", "supabase_client ="),
    ]

    for old, new in specific_fixes:
        content = content.replace(old, new)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    """Fonction principale."""
    test_files = []

    # Trouver tous les fichiers de test
    for root, _dirs, files in os.walk("tests"):
        for file in files:
            if file.endswith(".py"):
                test_files.append(os.path.join(root, file))

    # Ajouter d'autres fichiers problématiques
    other_files = [
        "src/jarvys_dev/tools/github_tools.py",
        "src/jarvys_dev/openai_data_importer.py",
    ]

    all_files = test_files + other_files

    for file_path in all_files:
        if os.path.exists(file_path):
            if fix_variable_prefixes(file_path):
                print(f"✅ Corrigé: {file_path}")
            else:
                print(f"ℹ️ Aucun changement: {file_path}")


if __name__ == "__main__":
    main()
