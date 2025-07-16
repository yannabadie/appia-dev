#!/usr/bin/env python3
"""Fix pyproject.toml ruff configuration"""


def fix_pyproject_ruff():
    """Fix ruff configuration in pyproject.toml"""
    with open("pyproject.toml", "r") as f:
        lines = f.readlines()

    fixed_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        # Skip the psutil line which is in wrong place
        if "psutil" in line and i > 0 and "[tool.ruff" in lines[i - 1]:
            skip_next = True
            continue

        if skip_next and line.strip() == "":
            skip_next = False
            continue

        fixed_lines.append(line)

    with open("pyproject.toml", "w") as f:
        f.writelines(fixed_lines)

    print("✅ Fixed pyproject.toml ruff configuration")


if __name__ == "__main__":
    fix_pyproject_ruff()
