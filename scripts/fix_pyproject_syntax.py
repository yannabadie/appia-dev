#!/usr/bin/env python3
"""Fix pyproject.toml syntax issues"""


def fix_pyproject_syntax():
    """Fix syntax issues in pyproject.toml"""
    try:
        with open("pyproject.toml", "r") as f:
            lines = f.readlines()

        fixed_lines = []
        in_dependencies = False

        for i, line in enumerate(lines):
            # Check if we're in the dependencies section
            if "dependencies = [" in line:
                in_dependencies = True
                fixed_lines.append(line)
                continue

            # If we're in dependencies and find a line without trailing comma
            if in_dependencies and line.strip() and line.strip() != "]":
                stripped = line.rstrip()
                # Add comma if missing and not the closing bracket
                if not stripped.endswith(",") and not stripped.endswith("]"):
                    if (
                        i + 1 < len(lines)
                        and lines[i + 1].strip()
                        and lines[i + 1].strip() != "]"
                    ):
                        line = stripped + ",\n"

            # Check for end of dependencies
            if in_dependencies and "]" in line and "[" not in line:
                in_dependencies = False

            fixed_lines.append(line)

        # Write back
        with open("pyproject.toml", "w") as f:
            f.writelines(fixed_lines)

        print("✅ Fixed pyproject.toml syntax")

        # Show the dependencies section for verification
        print("\n📋 Dependencies section:")
        in_deps = False
        for line in fixed_lines:
            if "dependencies = [" in line:
                in_deps = True
            if in_deps:
                print(line.rstrip())
            if in_deps and "]" in line and "[" not in line:
                break

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    fix_pyproject_syntax()
