from typing import Dict, List, Any, Optional
import json
import sys
import os
#!/usr/bin/env python3
"""Fix pyproject.toml conflicts"""

import re


def fix_pyproject():
    """Fix pyproject.toml file"""
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()

        # Remove all conflict markers
        content = re.sub(r"<<<<<<< HEAD\n", "", content)
        content = re.sub(r"=======\n", "", content)
        content = re.sub(r"
        # Ensure the file is valid TOML
        # Keep a clean version
        if "dependencies = [" in content:
            # Find and fix the dependencies section
            lines = content.splitlines()
            fixed_lines = []
            in_conflict = False

            for line in lines:
                if "<<<<<<< " in line or "=======" in line or "                    in_conflict = not in_conflict
                    continue
                if not in_conflict:
                    fixed_lines.append(line)

            content = "\n".join(fixed_lines)

        with open("pyproject.toml", "w") as f:
            f.write(content)

        print("✅ Fixed pyproject.toml")

    except Exception as e:
        print(f"❌ Error fixing pyproject.toml: {e}")


if __name__ == "__main__":
    fix_pyproject()
