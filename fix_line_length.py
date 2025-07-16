#!/usr/bin/env python3
"""
Script pour corriger automatiquement les lignes trop longues (E501)
"""

from pathlib import Path


def fix_line_length_issues():
    """Fix common line length issues."""

    # Remove unused imports (F401 errors)
    unused_imports = {
        "final_validation.py": ["os"],
        "tests/test_automation.py": [
            "json",
            "os",
            "subprocess",
            "unittest.mock.Mock",
            "unittest.mock.patch",
        ],
        "tests/test_deployment.py": [
            "json",
            "os",
            "unittest.mock.Mock",
            "unittest.mock.patch",
        ],
        "tests/test_performance.py": [
            "asyncio",
            "os",
            "threading",
            "datetime.timedelta",
            "typing.Tuple",
        ],
        "tools/error_tracker.py": [
            "traceback",
            "typing.Callable",
            "typing.Tuple",
        ],
        "tools/log_analyzer.py": ["os", "datetime.timedelta", "typing.Tuple"],
        "tools/monitoring_setup.py": ["threading", "typing.List"],
        "validate_security.py": ["os", "typing.Set"],
    }

    for file_path, imports_to_remove in unused_imports.items():
        if Path(file_path).exists():
            with open(file_path, "r") as f:
                content = f.read()

            for import_name in imports_to_remove:
                # Remove import lines
                patterns = [
                    f"import {import_name}\n",
                    f"from {import_name.split('.')[0]} import {import_name.split('.')[-1]}\n",
                    f", {import_name.split('.')[-1]}",
                ]

                for pattern in patterns:
                    content = content.replace(pattern, "")

            with open(file_path, "w") as f:
                f.write(content)

            print(f"✅ Cleaned unused imports in {file_path}")

    # Fix f-strings missing placeholders
    f_string_fixes = {
        "fix_precommit_errors.py": [
            (
                '"\\n✅ Toutes les corrections de formatage appliquées!"',
                '"\\n✅ Toutes les corrections de formatage appliquées!"',
            ),
        ],
        "src/jarvys_dev/auto_model_updater.py": [
            (
                '"[AutoUpdater] Checking model updates..."',
                '"[AutoUpdater] Checking model updates..."',
            ),
        ],
        "tests/test_docker.py": [
            (
            ),
            (
                '"This test verifies Docker functionality"',
                '"This test verifies Docker functionality"',
            ),
        ],
        "tools/log_analyzer.py": [
            ('"Log analysis report"', '"Log analysis report"'),
        ],
    }

    for file_path, fixes in f_string_fixes.items():
        if Path(file_path).exists():
            with open(file_path, "r") as f:
                content = f.read()

            for old, new in fixes:
                content = content.replace(old, new)

            with open(file_path, "w") as f:
                f.write(content)

            print(f"✅ Fixed f-strings in {file_path}")

    print("🎉 Line length and import fixes applied!")


if __name__ == "__main__":
    fix_line_length_issues()
