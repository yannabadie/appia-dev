#!/usr/bin/env python3
"""
Fix common linting errors in Python files.

This script automatically fixes common linting errors, particularly F821 (undefined name)
and F841 (unused variable) errors in Python files.

Usage:
    python fix_linting_errors.py [directory] [--dry-run]

Arguments:
    directory   - Directory to process recursively (default: deployment_packages/)
    --dry-run   - Only show what would be fixed without making changes

Examples:
    python fix_linting_errors.py                        # Fix errors in deployment_packages/
    python fix_linting_errors.py src/                   # Fix errors in src/
    python fix_linting_errors.py --dry-run              # Show what would be fixed in deployment_packages/
    python fix_linting_errors.py src/ --dry-run         # Show what would be fixed in src/
"""

import os
import re
import sys
from typing import Dict, List


def fix_f821_errors(content: str) -> str:
    """
    Fix F821 (undefined name) errors by replacing incorrect variable references.

    Args:
        content: The source code content to process

    Returns:
        Fixed content with corrected variable references
    """
    # Case 1: _response = ...; if response.
    content = re.sub(
        r"(_response = .*)(\n(.*\n)*?.*)(\n\s*if\s+)response\.",
        r"\1\2\4_response.",
        content,
    )
    content = re.sub(
        r"(_response = .*)(\n(.*\n)*?.*)(\n\s*data = )response\.",
        r"\1\2\4_response.",
        content,
    )
    content = re.sub(
        r"(_response = .*)(\n(.*\n)*?.*)(\n\s*return\s+)response\.",
        r"\1\2\4_response.",
        content,
    )
    content = re.sub(
        r'(_response = .*)(\n(.*\n)*?.*)(\n\s*logger = None\.error\(f".*){response\.',
        r"\1\2\4{_response.",
        content,
    )
    content = re.sub(
        r'(_response = .*)(\n(.*\n)*?.*)(\n\s*logger = None\.warning\(f".*){response\.',
        r"\1\2\4{_response.",
        content,
    )
    content = re.sub(
        r'(_response = .*)(\n(.*\n)*?.*)(\n\s*logger = None\.info\(f".*){response\[:50]}..."\)',
        r'\1\2\4{_response[:50]}...")',
        content,
    )

    # Case 2: _result = ...; if result.
    content = re.sub(
        r"(_result = .*)(\n(.*\n)*?.*)(\n\s*if\s+)result\.", r"\1\2\4_result.", content
    )
    content = re.sub(
        r'(_result = .*)(\n(.*\n)*?.*)(\n\s*logger = None\.error\(f".*){result\.',
        r"\1\2\4{_result.",
        content,
    )
    content = re.sub(
        r'(_result = .*)(\n(.*\n)*?.*)(\n\s*logger = None\.warning\(f".*){result\.',
        r"\1\2\4{_result.",
        content,
    )
    content = re.sub(
        r'(_result = .*)(\n(.*\n)*?.*)(\n\s*raise Exception\(f".*){result\.',
        r"\1\2\4{_result.",
        content,
    )

    # Case 3: ai_response = ...; use of response
    content = re.sub(
        r"(ai_response = .*)(\n(.*\n)*?.*)(\n\s*await self\.digital_twin\.update_interaction\(command, )response,",
        r"\1\2\4ai_response,",
        content,
    )
    content = re.sub(
        r"(ai_response = .*)(\n(.*\n)*?.*)(\n\s*return )response",
        r"\1\2\4ai_response",
        content,
    )
    content = re.sub(
        r"(ai_response = .*)(\n(.*\n)*?.*)(\n\s*await self\.speak\()response\)",
        r"\1\2\4ai_response)",
        content,
    )
    content = re.sub(
        r'(ai_response = .*)(\n(.*\n)*?.*)(\n\s*self\.test_results\[.*\] = {\n(.*\n)*?.*"response_length": len\()response\)',
        r"\1\2\4ai_response)",
        content,
    )
    content = re.sub(
        r'(ai_response = .*)(\n(.*\n)*?.*)(\n\s*logger = None\.info\(f".*len\()response\)',
        r"\1\2\4ai_response)",
        content,
    )

    # Other specific cases for undefined 'response'
    content = re.sub(r'response \+= f"', 'response_str += f"', content)
    content = re.sub(r'response = ""', 'response_str = ""', content)
    content = re.sub(r"return response", "return response_str", content)

    return content


def fix_f841_errors(content: str) -> str:
    """
    Fix F841 (unused variable) errors by commenting out unused variable assignments.

    Args:
        content: The source code content to process

    Returns:
        Fixed content with commented out unused variables
    """
    # Comment out unused variables
    unused_patterns = [
        r"^(\s*)(update = {.*)",
        r"^(\s*)(alert = {.*)",
        r"^(\s*)(total_cost = sum\(.*\))",
        r'^(\s*)(backup_id = f".*")',
        r"^(\s*)(active_servers = sum\(.*\))",
        r"^(\s*)(total_servers = len\(.*\))",
        r"^(\s*)(stats = await self\.get_cloud_stats\(\))",
        r"^(\s*)(stats = await self\.get_email_stats\(\))",
        r"^(\s*)(file_found = file_info)",
        r'^(\s*)(action_fr = "copié" if .* else "déplacé")',
        r"^(\s*)(stats = await self\.get_file_stats\(\))",
        r"^(\s*)(stats = self\.get_voice_stats\(\))",
        r'^(\s*)(status = "🟢 Active" if .* else "🔴 Inactive")',
    ]

    for pattern in unused_patterns:
        content = re.sub(pattern, r"\1# \2", content, flags=re.MULTILINE)

    return content


def fix_linting_errors(directory: str, dry_run: bool = False) -> Dict[str, List[str]]:
    """
    Fix linting errors in all Python files under the specified directory.

    Args:
        directory: The directory to process recursively
        dry_run: If True, only report potential changes without modifying files

    Returns:
        A dictionary with statistics on fixed files and errors
    """
    results = {"fixed_files": [], "error_files": [], "skipped_files": []}

    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        return results

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    original_content = content
                    content = fix_f821_errors(content)
                    content = fix_f841_errors(content)

                    if content != original_content:
                        if dry_run:
                            print(f"Would fix: {filepath}")
                            results["skipped_files"].append(filepath)
                        else:
                            print(f"Fixing {filepath}")
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(content)
                            results["fixed_files"].append(filepath)
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")
                    results["error_files"].append(filepath)

    return results


if __name__ == "__main__":
    # Parse command line arguments
    dry_run = "--dry-run" in sys.argv

    # Get the target directory from command line arguments or use default
    target_dir = "deployment_packages/"
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            target_dir = arg
            break

    # Run the linting error fixes
    results = fix_linting_errors(target_dir, dry_run)

    # Print summary
    print("\nSummary:")
    print(f"- Fixed files: {len(results['fixed_files'])}")
    print(f"- Error files: {len(results['error_files'])}")
    if dry_run:
        print(f"- Files that would be fixed (dry run): {len(results['skipped_files'])}")

    print("Done.")
