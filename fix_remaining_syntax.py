#!/usr/bin/env python3
"""
🔧 CORRECTION FINALE: Réparer les dernières erreurs de syntaxe empêchant le commit
"""

import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_dashboard_local():
    """Réparer dashboard_local/dashboard_local.py"""
    file_path = "dashboard_local/dashboard_local.py"
    logger.info(f"🔧 Fixing {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix double Flask assignment
        content = re.sub(
            r"app = Flask\(__name__\) = Flask\(__name__\)",
            "app = Flask(__name__)",
            content,
        )

        # Fix decorator syntax with assignment
        content = re.sub(
            r'@app = Flask\(__name__\)\.route\("([^"]+)"\)',
            r'@app.route("\1")',
            content,
        )

        content = re.sub(
            r'@app = Flask\(__name__\)\.route\("([^"]+)", methods=\["([^"]+)"\]\)',
            r'@app.route("\1", methods=["\2"])',
            content,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ Fixed {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {e}")


def fix_enhanced_fallback_engine():
    """Réparer jarvys_ai/enhanced_fallback_engine.py"""
    file_path = "jarvys_ai/enhanced_fallback_engine.py"
    logger.info(f"🔧 Fixing {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix the malformed f-string
        content = re.sub(
            r'logger\.error\(f"❌ Error validating cloud config = \{\}: \{e\}"\)',
            'logger.error(f"❌ Error validating cloud config: {e}")',
            content,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ Fixed {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {e}")


def fix_test_workflows():
    """Réparer test_workflows.py"""
    file_path = "test_workflows.py"
    logger.info(f"🔧 Fixing {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Reconstruire le fichier avec indentation correcte
        new_lines = []
        in_subprocess_call = False

        for i, line in enumerate(lines):
            # Fix indentation issues around subprocess.run
            if "subprocess.run(" in line:
                new_lines.append(line)
                in_subprocess_call = True
            elif in_subprocess_call and "capture_output=True," in line:
                new_lines.append("            capture_output=True,\n")
            elif in_subprocess_call and "text=True," in line:
                new_lines.append("            text=True,\n")
            elif in_subprocess_call and 'cwd="/workspaces/appia-dev",' in line:
                new_lines.append('            cwd="/workspaces/appia-dev",\n')
            elif in_subprocess_call and line.strip() == ")":
                new_lines.append("        )\n")
                in_subprocess_call = False
            elif 'if __name__ == "__main__":' in line:
                new_lines.append('if __name__ == "__main__":\n')
            elif line.strip() == "exit(main())" and i > 0:
                new_lines.append("    exit(main())\n")
            else:
                new_lines.append(line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        logger.info(f"✅ Fixed {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {e}")


def fix_test_deployment():
    """Réparer tests/test_deployment.py"""
    file_path = "tests/test_deployment.py"
    logger.info(f"🔧 Fixing {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix config assignment in conditional
        content = re.sub(
            r'if "timeout" in config = \{\}:',
            'config = {}\n        if "timeout" in config:',
            content,
        )

        # Fix config assignment in assertion
        content = re.sub(
            r'config = \{\} or "docs" in str\(\s*config = \{\}',
            'config.get("docs_dir", "") or "docs" in str(config',
            content,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ Fixed {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {e}")


def fix_test_jarvys_dev():
    """Réparer tests/test_jarvys_dev.py"""
    file_path = "tests/test_jarvys_dev.py"
    logger.info(f"🔧 Fixing {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix malformed f-string
        content = re.sub(
            r'pytest\.fail\(f"Model config = \{\} loading failed: \{e\}"\)',
            'pytest.fail(f"Model config loading failed: {e}")',
            content,
        )

        # Fix invalid assertion syntax
        content = re.sub(
            r"assert isinstance\(app = None, FastAPI\)",
            "assert isinstance(app, FastAPI)",
            content,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ Fixed {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {e}")


def fix_error_tracker():
    """Réparer tools/error_tracker.py"""
    file_path = "tools/error_tracker.py"
    logger.info(f"🔧 Fixing {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix list comprehension with line continuation
        content = re.sub(
            r'context = \[\s*f"\{_i\+1\}: \{lines\[_i\]\.rstrip\(\)\}"\\\n\s*for _i in range\(context_start, context_end\)\s*\]',
            'context = [\n                            f"{_i+1}: {lines[_i].rstrip()}"\n                            for _i in range(context_start, context_end)\n                        ]',
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ Fixed {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {e}")


def fix_create_deployment_package():
    """Réparer create_deployment_package.py logger assignments"""
    file_path = "create_deployment_package.py"
    logger.info(f"🔧 Fixing {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix logger assignments to actual logging calls
        patterns = [
            (
                r'logger = logging\.getLogger\(__name__\)\.error\(\s*f"([^"]+)"\s*\)',
                r'logging.getLogger(__name__).error(f"\1")',
            ),
            (
                r'logger = logging\.getLogger\(__name__\)\.info\("([^"]+)"\)',
                r'logging.getLogger(__name__).info("\1")',
            ),
            (
                r'logger = logging\.getLogger\(__name__\)\.info\(\s*f"([^"]+)"\s*\)',
                r'logging.getLogger(__name__).info(f"\1")',
            ),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ Fixed {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {e}")


def fix_continuous_improvement():
    """Réparer jarvys_ai/continuous_improvement.py"""
    file_path = "jarvys_ai/continuous_improvement.py"
    logger.info(f"🔧 Fixing {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix config assignment
        content = re.sub(
            r'self\.demo_mode = config = \{\}\.get\("demo_mode", True\)',
            'self.demo_mode = config.get("demo_mode", True) if config else True',
            content,
        )

        # Fix response variable issues
        content = re.sub(
            r"_response = requests\.get\([^)]+\)\s*if response\.status_code",
            "_response = requests.get(url, headers=headers, params=params, timeout=30)\n\n            if _response.status_code",
            content,
        )

        content = re.sub(
            r"return response\.json\(\)", "return _response.json()", content
        )

        content = re.sub(r"response\.status_code", "_response.status_code", content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ Fixed {file_path}")

    except Exception as e:
        logger.error(f"❌ Error fixing {file_path}: {e}")


def main():
    """Exécuter toutes les corrections"""
    logger.info("🚀 Début des corrections finales...")

    fixes = [
        fix_dashboard_local,
        fix_enhanced_fallback_engine,
        fix_test_workflows,
        fix_test_deployment,
        fix_test_jarvys_dev,
        fix_error_tracker,
        fix_create_deployment_package,
        fix_continuous_improvement,
    ]

    for fix_func in fixes:
        try:
            fix_func()
        except Exception as e:
            logger.error(f"❌ Error in {fix_func.__name__}: {e}")

    logger.info("✅ Corrections terminées!")


if __name__ == "__main__":
    main()
