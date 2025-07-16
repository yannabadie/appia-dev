#!/usr/bin/env python3
"""Clean all remaining merge conflicts in the codebase"""

import glob
import re


def clean_conflict_markers(content):
    """Remove all conflict markers from content"""
    # Pattern to match conflict blocks
    conflict_pattern = re.compile(
        r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]+", re.DOTALL | re.MULTILINE
    )

    # Keep HEAD version (ours) for all conflicts
    resolved = conflict_pattern.sub(lambda m: m.group(1), content)

    # Also clean any remaining markers
    resolved = re.sub(r"<<<<<<< HEAD\n", "", resolved)
    resolved = re.sub(r"=======\n", "", resolved)
    resolved = re.sub(r">>>>>>> .*\n", "", resolved)
    return resolved


def find_files_with_conflicts():
    """Find all files with conflict markers"""
    conflicted_files = []

    # Search patterns
    patterns = [
        "**/*.py",
        "**/*.yaml",
        "**/*.yml",
        "**/*.toml",
        "**/*.json",
        "**/*.sh",
        "**/*.md",
        "**/*.txt",
    ]

    for pattern in patterns:
        for filepath in glob.glob(pattern, recursive=True):
            # Skip certain directories
            if any(
                skip in filepath
                for skip in [".git/", "__pycache__/", ".venv/", "node_modules/"]
            ):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "<<<<<<< HEAD" in content:
                        conflicted_files.append(filepath)
            except Exception:
                pass

    return conflicted_files


def fix_file(filepath):
    """Fix conflicts in a single file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if "<<<<<<< HEAD" in content:
            resolved_content = clean_conflict_markers(content)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(resolved_content)

            return True
        return False

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False


def main():
    """Main function"""
    print("🔍 Searching for files with merge conflicts...")

    conflicted_files = find_files_with_conflicts()

    if not conflicted_files:
        print("✅ No files with conflicts found!")
        return

    print(f"📁 Found {len(conflicted_files)} files with conflicts:")
    for f in conflicted_files:
        print(f"  - {f}")

    print("\n🧹 Cleaning conflicts...")

    fixed_count = 0
    for filepath in conflicted_files:
        print(f"  Fixing {filepath}...", end="")
        if fix_file(filepath):
            print(" ✅")
            fixed_count += 1
        else:
            print(" ❌")

    print(f"\n✅ Fixed {fixed_count}/{len(conflicted_files)} files!")


if __name__ == "__main__":
    main()
