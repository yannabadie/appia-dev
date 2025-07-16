import json
import sys
from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""Resolve all merge conflicts automatically"""

import os
import re
import subprocess


def get_all_conflicted_files():
    """Get all files with conflicts"""
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    conflicts = []
    for line in result.stdout.splitlines():
        if line.startswith("UU "):
            conflicts.append(line[3:].strip())
    return conflicts


def resolve_conflict_markers(content):
    """Remove conflict markers and keep our version"""
    # Pattern to match conflict blocks
    conflict_pattern = re.compile(
        r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n    )

    # Keep HEAD version (ours) for all conflicts
    resolved = conflict_pattern.sub(lambda m: m.group(1), content)
    return resolved


def fix_file(filepath):
    """Fix conflicts in a single file"""
    print(f"🔧 Fixing conflicts in {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if file has conflicts
        if "<<<<<<< HEAD" in content:
            resolved_content = resolve_conflict_markers(content)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(resolved_content)

            print(f"✅ Resolved conflicts in {filepath}")
            return True
        else:
            print(f"ℹ️  No conflicts found in {filepath}")
            return False

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False


def main():
    """Main function"""
    conflicts = get_all_conflicted_files()

    if not conflicts:
        print("✅ No conflicted files found!")
        return

    print(f"🔍 Found {len(conflicts)} conflicted files")
    print("Resolving conflicts by keeping HEAD version (ours)...\n")

    resolved_count = 0
    for filepath in conflicts:
        if os.path.exists(filepath):
            if fix_file(filepath):
                resolved_count += 1
                # Stage the resolved file
                subprocess.run(["git", "add", filepath])

    print(f"\n✅ Resolved {resolved_count} files!")
    print("Now run: git status")


if __name__ == "__main__":
    main()
