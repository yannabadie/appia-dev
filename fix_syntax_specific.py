#!/usr/bin/env python3
"""
Script spécialisé pour corriger les erreurs de syntaxe introduites par la correction automatique
"""

import os
import re
import subprocess

def fix_syntax_patterns(file_path):
    """Corriger les patterns de syntaxe incorrects spécifiques"""
    if not os.path.exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_content = content
    
    # Corrections spécifiques pour les erreurs introduites
    
    # 1. Corriger les assignations incorrectes avec 'app = None'
    content = re.sub(r'@app = None\.', '@app.', content)
    content = re.sub(r'app = None\.(.*)', r'app.\1', content)
    content = re.sub(r'client = None\.(.*)', r'client.\1', content)
    content = re.sub(r'config = {}\[(.*)', r'config[\1', content)
    
    # 2. Corriger les imports incorrects
    content = re.sub(r'from (.+) import (.+)', r'from \1 import \2', content)
    content = re.sub(r'from (.+)=None\.(.+) import (.+)', r'from \1.\2 import \3', content)
    content = re.sub(r'import', 'import', content)
    
    # 3. Corriger les définitions de fonction avec paramètres incorrects
    content = re.sub(r'def ([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*), config = {}: ([^)]*)\)', 
                     r'def \1(\2, config: \3 = None)', content)
    content = re.sub(r'def ([a-zA-Z_][a-zA-Z0-9_]*)\(config = {}: ([^)]*)\)', 
                     r'def \1(config: \2 = None)', content)
    content = re.sub(r'client = None: ([A-Za-z]+)', r'client: \1', content)
    
    # 4. Corriger les assignations avec égalité incorrecte
    content = re.sub(r'if config = {}\[', 'if config[', content)
    content = re.sub(r'config = ', 'config = ', content)
    content = re.sub(r'client = ', 'client = ', content)
    content = re.sub(r'app = ', 'app = ', content)
    
    # 5. Corriger les boucles for incorrectes
    content = re.sub(r'for (.+) in config = {}\.items\(\):', r'for \1 in config.items():', content)
    
    # 6. Corriger les chaînes de caractères cassées
    content = re.sub(r'resolved = re\.sub\(r\'    $', "resolved = re.sub(r'>>>>>>> .*\\n', '', resolved)", content, flags=re.MULTILINE)
    
    # 7. Corriger les imports d'app spécifiques
    content = re.sub(r'from app=None\.main', 'from app.main', content)
    
    # 8. Corriger les expressions f-string cassées
    content = re.sub(r'f"(.*)config"', r'f"\1config"', content)
    
    # 9. Corriger les patterns de variables spécifiques
    content = re.sub(r'logger = None$', 'logger = logging.getLogger(__name__)', content, flags=re.MULTILINE)
    content = re.sub(r'client = None$', 'client = None  # To be initialized', content, flags=re.MULTILINE)
    content = re.sub(r'app = None$', 'app = None  # To be initialized', content, flags=re.MULTILINE)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Fonction principale"""
    print("🔧 Correction des erreurs de syntaxe spécifiques...")
    
    # Compter les erreurs de syntaxe avant
    result_before = subprocess.run(
        ["poetry", "run", "ruff", "check", ".", "--statistics"],
        capture_output=True,
        text=True,
        cwd="/workspaces/appia-dev"
    )
    
    syntax_errors_before = 0
    for line in result_before.stdout.split('\n'):
        if 'syntax-error' in line:
            try:
                syntax_errors_before = int(line.split()[0])
            except:
                pass
            break
    
    print(f"Erreurs de syntaxe avant correction: {syntax_errors_before}")
    
    # Corriger les fichiers Python
    files_fixed = 0
    for root, dirs, files in os.walk("/workspaces/appia-dev"):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_syntax_patterns(file_path):
                    files_fixed += 1
                    print(f"Corrigé: {file_path}")
    
    print(f"\nFichiers corrigés: {files_fixed}")
    
    # Compter les erreurs après
    result_after = subprocess.run(
        ["poetry", "run", "ruff", "check", ".", "--statistics"],
        capture_output=True,
        text=True,
        cwd="/workspaces/appia-dev"
    )
    
    syntax_errors_after = 0
    for line in result_after.stdout.split('\n'):
        if 'syntax-error' in line:
            try:
                syntax_errors_after = int(line.split()[0])
            except:
                pass
            break
    
    print(f"Erreurs de syntaxe après correction: {syntax_errors_after}")
    print(f"Erreurs réduites: {syntax_errors_before - syntax_errors_after}")

if __name__ == "__main__":
    main()
