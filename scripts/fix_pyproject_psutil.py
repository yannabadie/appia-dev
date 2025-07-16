#!/usr/bin/env python3
"""Fix pyproject.toml to remove invalid psutil field"""


def fix_pyproject():
    """Remove psutil from wrong location in pyproject.toml"""
    with open("pyproject.toml", "r") as f:
        lines = f.readlines()

    fixed_lines = []
    in_ruff_lint = False

    for i, line in enumerate(lines):
        # Check if we're in [tool.ruff.lint] section
        if line.strip() == "[tool.ruff.lint]":
            in_ruff_lint = True
            fixed_lines.append(line)
            continue

        # Check if we're leaving the ruff.lint section
        if in_ruff_lint and line.startswith("[") and line.strip() != "[tool.ruff.lint]":
            in_ruff_lint = False

        # Skip psutil line if it's in the wrong place
        if in_ruff_lint and "psutil" in line and not line.strip().startswith("#"):
            print(f"  Removing invalid line: {line.strip()}")
            continue

        fixed_lines.append(line)

    # Write back
    with open("pyproject.toml", "w") as f:
        f.writelines(fixed_lines)

    print("✅ Fixed pyproject.toml - removed psutil from ruff config = {}")


if __name__ == "__main__":
    fix_pyproject()
