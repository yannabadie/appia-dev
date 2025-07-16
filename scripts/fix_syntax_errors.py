#!/usr/bin/env python3
"""Fix syntax errors in Python files"""


def fix_test_workflows():
    """Fix test_workflows.py syntax error"""
    with open("test_workflows.py", "r") as f:
        content = f.read()

    # Fix the missing closing bracket
    content = content.replace(
        '["poetry", "run", "python", "scripts/generate_wiki_docs.py"],',
        '["poetry", "run", "python", "scripts/generate_wiki_docs.py"],',
    )

    with open("test_workflows.py", "w") as f:
        f.write(content)

    print("✅ Fixed test_workflows.py")


def fix_clean_conflicts():
    """Fix scripts/clean_all_conflicts.py regex syntax"""
    with open("scripts/clean_all_conflicts.py", "r") as f:
        content = f.read()

    # Fix the broken regex
    content = content.replace(
        "r'<<<<<<< HEAD\\n(.*?)\\n=======\\n(.*?)\\n        re.DOTALL | re.MULTILINE",
        "r'<<<<<<< HEAD\\n(.*?)\\n=======\\n(.*?)\\n>>>>>>> [^\\n]+',\n        re.DOTALL | re.MULTILINE",
    )

    with open("scripts/clean_all_conflicts.py", "w") as f:
        f.write(content)

    print("✅ Fixed scripts/clean_all_conflicts.py")


if __name__ == "__main__":
    fix_test_workflows()
    fix_clean_conflicts()
