#!/usr/bin/env python3
"""Resolve merge conflicts intelligently"""

import os
import re
import subprocess


def get_conflicted_files():
    """Get list of conflicted files"""
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    conflicts = []
    for line in result.stdout.splitlines():
        if line.startswith("UU "):
            conflicts.append(line[3:])
    return conflicts


def resolve_file(filepath):
    """Resolve conflicts in a single file"""
    print(f"🔧 Resolving conflicts in {filepath}")

    with open(filepath, "r") as f:
        content = f.read()

    # Pattern to find conflict markers
    conflict_pattern = re.compile(
        r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n    )

    def resolve_conflict(match):
        ours = match.group(1)
        theirs = match.group(2)

        # For Python files, prefer the version with proper formatting
        if filepath.endswith(".py"):
            # If one version has proper line length, prefer it
            if all(len(line) <= 79 for line in ours.splitlines()):
                return ours
            elif all(len(line) <= 79 for line in theirs.splitlines()):
                return theirs

            # Otherwise, keep ours (our linting fixes)
            return ours

        # For config files, keep ours
        if filepath in [".gitignore", ".pre-commit-config.yaml"]:
            return ours

        # Default to theirs for other files
        return theirs

    # Resolve all conflicts
    resolved_content = conflict_pattern.sub(resolve_conflict, content)

    # Write back
    with open(filepath, "w") as f:
        f.write(resolved_content)

    # Stage the resolved file
    subprocess.run(["git", "add", filepath])
    print(f"✅ Resolved and staged {filepath}")


def main():
    """Main function"""
    conflicts = get_conflicted_files()

    if not conflicts:
        print("✅ No conflicts found!")
        return

    print(f"🔍 Found {len(conflicts)} conflicted files")

    for filepath in conflicts:
        if os.path.exists(filepath):
            resolve_file(filepath)

    print("\n✅ All conflicts resolved!")
    print("Run 'git status' to verify and then commit the merge")


if __name__ == "__main__":
    main()
