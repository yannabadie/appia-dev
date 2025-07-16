#!/usr/bin/env python3
"""Verify all linting errors are fixed"""

import subprocess
import sys


def check_linting():
    """Run all linting checks and report results"""

    print("🔍 Running linting checks...\n")

    # Run ruff check
    result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Ruff check passed - No errors found!")
        return True
    else:
        print("❌ Ruff check failed. Errors found:")
        print(result.stdout)

        # Count error types
        error_types = {}
        for line in result.stdout.splitlines():
            if ": " in line and " " in line.split(": ")[1]:
                error_code = line.split(": ")[1].split(" ")[0]
                error_types[error_code] = error_types.get(error_code, 0) + 1

        print("\n📊 Error Summary:")
        for error_code, count in sorted(error_types.items()):
            print(f"  {error_code}: {count} errors")

        return False


def check_black():
    """Check black formatting"""
    print("\n🎨 Checking black formatting...")
    result = subprocess.run(["black", "--check", "."], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Black formatting check passed!")
        return True
    else:
        print("❌ Black formatting issues found")
        print("Run 'black .' to fix")
        return False


def check_isort():
    """Check import sorting"""
    print("\n📦 Checking import sorting...")
    result = subprocess.run(
        ["isort", "--check-only", "."], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ Import sorting check passed!")
        return True
    else:
        print("❌ Import sorting issues found")
        print("Run 'isort .' to fix")
        return False


if __name__ == "__main__":
    all_passed = True

    all_passed &= check_linting()
    all_passed &= check_black()
    all_passed &= check_isort()

    if all_passed:
        print("\n🎉 All linting checks passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)
