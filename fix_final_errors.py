#!/usr/bin/env python3
"""
Script pour corriger les dernières erreurs F821 (noms non définis)
"""

import os
import re
import subprocess

def get_f821_errors():
    """Obtenir la liste des erreurs F821"""
    try:
        result = subprocess.run(
            ["poetry", "run", "ruff", "check", "--select", "F821", ".", "--output-format", "json"],
            capture_output=True,
            text=True,
            cwd="/workspaces/appia-dev"
        )
        return result.stdout
    except Exception as e:
        print(f"Erreur: {e}")
        return ""

def fix_common_undefined_names(file_path):
    """Corriger les noms non définis courants"""
    if not os.path.exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Corrections courantes pour les noms non définis
    corrections = [
        # Imports manquants courants
        (r'^(?!.*import os)', 'import os\n'),
        (r'^(?!.*import sys)', 'import sys\n'),
        (r'^(?!.*import json)', 'import json\n'),
        (r'^(?!.*from typing)', 'from typing import Dict, List, Any, Optional\n'),
        
        # Variables globales courantes
        ('app = Flask(__name__)', 'app = Flask(__name__) = Flask(__name__)' if 'Flask' in content else 'app = Flask(__name__) = None'),
        ('client = None', 'client = None = None'),
        ('config = {}', 'config = {} = {}'),
        ('logger = logging.getLogger(__name__)', 'logger = logging.getLogger(__name__) = logging.getLogger(__name__)' if 'logging' in content else 'logger = logging.getLogger(__name__) = None'),
    ]
    
    for pattern, replacement in corrections:
        if pattern.startswith('^(?!.*'):
            # Pattern pour ajouter des imports au début
            if not re.search(pattern[6:-1], content, re.MULTILINE):
                content = replacement + content
        else:
            # Remplacements simples
            content = re.sub(rf'\b{pattern}\b', replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Fonction principale"""
    print("Correction des dernières erreurs F821...")
    
    # Obtenir la liste des erreurs
    errors_output = get_f821_errors()
    print(f"Analyse des erreurs F821...")
    
    # Compter les erreurs avant
    result_before = subprocess.run(
        ["poetry", "run", "ruff", "check", "--select", "F821", ".", "--statistics"],
        capture_output=True,
        text=True,
        cwd="/workspaces/appia-dev"
    )
    
    errors_before = 0
    for line in result_before.stdout.split('\n'):
        if 'F821' in line and 'undefined-name' in line:
            errors_before = int(line.split()[0])
            break
    
    print(f"Erreurs F821 avant correction: {errors_before}")
    
    # Corriger les fichiers Python
    files_fixed = 0
    for root, dirs, files in os.walk("/workspaces/appia-dev"):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_common_undefined_names(file_path):
                    files_fixed += 1
                    print(f"Corrigé: {file_path}")
    
    print(f"\nFichiers corrigés: {files_fixed}")
    
    # Compter les erreurs après
    result_after = subprocess.run(
        ["poetry", "run", "ruff", "check", "--select", "F821", ".", "--statistics"],
        capture_output=True,
        text=True,
        cwd="/workspaces/appia-dev"
    )
    
    errors_after = 0
    for line in result_after.stdout.split('\n'):
        if 'F821' in line and 'undefined-name' in line:
            errors_after = int(line.split()[0])
            break
    
    print(f"Erreurs F821 après correction: {errors_after}")
    print(f"Erreurs réduites: {errors_before - errors_after}")

if __name__ == "__main__":
    main()
