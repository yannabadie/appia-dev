#!/usr/bin/env python3
"""
Validation script for secrets usage and error handling across the repository.
Checks for proper environment variable usage and deprecated tokens.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set


def scan_file_for_patterns(file_path: Path, patterns: Dict[str, str]) -> Dict[str, List[str]]:
    """Scan a file for specific patterns and return matches."""
    results = {pattern_name: [] for pattern_name in patterns.keys()}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                results[pattern_name].extend(matches)
                
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        
    return results


def validate_repository() -> bool:
    """Validate the entire repository for secrets usage and error handling."""
    repo_root = Path.cwd()
    
    # Patterns to search for
    patterns = {
        'deprecated_supabase_token': r'SUPABASE_ACCESS_TOKEN',
        'openai_api_key': r'OPENAI_API_KEY',
        'github_token': r'GH_TOKEN|GITHUB_TOKEN',
        'supabase_service_role': r'SUPABASE_SERVICE_ROLE',
        'error_handling': r'try:|except|raise|RuntimeError|Exception',
        'env_var_access': r'os\.getenv|os\.environ',
    }
    
    # File extensions to scan
    extensions = {'.py', '.yml', '.yaml', '.sh', '.js', '.ts'}
    
    # Files to scan
    files_to_scan = []
    for ext in extensions:
        files_to_scan.extend(repo_root.rglob(f'*{ext}'))
    
    # Filter out virtual environments and build artifacts
    exclude_dirs = {'.venv', 'node_modules', '.git', '__pycache__', 'dist', 'build'}
    exclude_files = {'validate_security.py'}  # Exclude this validation script itself
    files_to_scan = [
        f for f in files_to_scan 
        if not any(part in exclude_dirs for part in f.parts)
        and f.name not in exclude_files
    ]
    
    print(f"🔍 Scanning {len(files_to_scan)} files for secrets usage and error handling...")
    
    deprecated_token_files = []
    files_with_good_error_handling = []
    files_with_proper_env_access = []
    
    for file_path in files_to_scan:
        results = scan_file_for_patterns(file_path, patterns)
        
        # Check for deprecated tokens
        if results['deprecated_supabase_token']:
            deprecated_token_files.append(file_path)
            
        # Check for error handling
        if results['error_handling']:
            files_with_good_error_handling.append(file_path)
            
        # Check for proper environment variable access
        if results['env_var_access']:
            files_with_proper_env_access.append(file_path)
    
    # Report results
    print("\n📊 Validation Results:")
    print("=" * 50)
    
    if deprecated_token_files:
        print(f"❌ Found {len(deprecated_token_files)} files with deprecated SUPABASE_ACCESS_TOKEN:")
        for f in deprecated_token_files:
            print(f"   - {f}")
        return False
    else:
        print("✅ No deprecated SUPABASE_ACCESS_TOKEN found")
    
    print(f"✅ Found {len(files_with_good_error_handling)} files with error handling")
    print(f"✅ Found {len(files_with_proper_env_access)} files with proper env var access")
    
    # Validate workflow files specifically
    workflow_dir = repo_root / '.github' / 'workflows'
    if workflow_dir.exists():
        workflow_files = list(workflow_dir.glob('*.yml'))
        firewall_configs = 0
        
        for wf_file in workflow_files:
            with open(wf_file, 'r') as f:
                content = f.read()
                if 'Configure Firewall' in content and 'github.com' in content:
                    firewall_configs += 1
        
        print(f"✅ Found {firewall_configs}/{len(workflow_files)} workflows with firewall configuration")
        
        if firewall_configs == len(workflow_files):
            print("🎉 All workflows have proper firewall configuration!")
        else:
            missing = len(workflow_files) - firewall_configs
            print(f"⚠️  {missing} workflows are missing firewall configuration")
    
    return True


if __name__ == "__main__":
    print("🔒 Repository Security and Configuration Validation")
    print("=" * 60)
    
    success = validate_repository()
    
    if success:
        print("\n🎉 Repository validation passed!")
        sys.exit(0)
    else:
        print("\n💥 Repository validation failed!")
        sys.exit(1)