#!/usr/bin/env python3
"""Rebuild pyproject.toml dependencies section"""


def rebuild_dependencies():
    """Rebuild the dependencies section of pyproject.toml"""
    # Read the file
    with open("pyproject.toml", "r") as f:
        content = f.read()

    # Find dependencies section
    import re

    # Extract all dependencies
    deps_pattern = r'"([^"]+>=?[^"]+)"'
    dependencies = re.findall(deps_pattern, content)

    # Remove duplicates while preserving order
    seen = set()
    unique_deps = []
    for dep in dependencies:
        if dep not in seen:
            seen.add(dep)
            unique_deps.append(dep)

    # Build clean dependencies list
    deps_str = "dependencies = [\n"
    for i, dep in enumerate(unique_deps):
        deps_str += f'    "{dep}"'
        if i < len(unique_deps) - 1:
            deps_str += ","
        deps_str += "\n"
    deps_str += "]"

    # Replace the dependencies section
    # Find the start and end of dependencies
    start_idx = content.find("dependencies = [")
    if start_idx == -1:
        print("❌ Could not find dependencies section")
        return

    # Find the matching closing bracket
    bracket_count = 0
    end_idx = start_idx
    for i in range(start_idx, len(content)):
        if content[i] == "[":
            bracket_count += 1
        elif content[i] == "]":
            bracket_count -= 1
            if bracket_count == 0:
                end_idx = i + 1
                break

    # Replace the section
    new_content = content[:start_idx] + deps_str + content[end_idx:]

    # Write back
    with open("pyproject.toml", "w") as f:
        f.write(new_content)

    print("✅ Rebuilt dependencies section")
    print(f"📦 Found {len(unique_deps)} unique dependencies")


if __name__ == "__main__":
    rebuild_dependencies()
