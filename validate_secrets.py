#!/usr/bin/env python3
"""
Script de validation de la cohérence des noms de secrets d'environnement.
Vérifie que tous les secrets utilisés dans le code correspondent aux secrets déclarés.
"""

import re
from collections import defaultdict
from pathlib import Path


def extract_secrets_from_file(filepath):
    """Extrait tous les secrets d'environnement d'un fichier."""
    secrets = set()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Patterns pour détecter les secrets
        patterns = [
            r'os\.getenv\(["\']([^"\']+)["\']\)',  # os.getenv("SECRET")
            r'os\.environ\[["\']([^"\']+)["\']\]',  # os.environ["SECRET"]
            r'getenv\(["\']([^"\']+)["\']\)',  # getenv("SECRET")
            r"secrets\.([A-Z_]+)",  # secrets.SECRET_NAME
            r'Deno\.env\.get\(["\']([^"\']+)["\']\)',  # Deno.env.get("SECRET")
            r"\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}",  # ${{ secrets.SECRET }}
            r"\$\{localEnv:([A-Z_]+)\}",  # ${localEnv:SECRET}
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Ignorer les exemples génériques
                if match in ["SECRET_NAME", "VARIABLE_NAME", "SECRET"]:
                    continue
                if match and match.isupper() and "_" in match:
                    secrets.add(match)

    except Exception as e:
        print(f"Erreur lecture {filepath}: {e}")

    return secrets


def load_declared_secrets():
    """Charge la liste des secrets déclarés depuis source_secrets.txt."""
    secrets_file = Path(__file__).parent / "source_secrets.txt"
    declared_secrets = set()

    if secrets_file.exists():
        with open(secrets_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Format: SECRET_NAME<tab>timestamp
                    secret_name = line.split("\t")[0]
                    if secret_name:
                        declared_secrets.add(secret_name)

    return declared_secrets


def scan_repository():
    """Scanne tout le repository pour les secrets utilisés."""
    repo_root = Path(__file__).parent
    used_secrets = defaultdict(list)

    # Patterns de fichiers à scanner
    file_patterns = [
        "**/*.py",
        "**/*.yml",
        "**/*.yaml",
        "**/*.ts",
        "**/*.js",
        "**/*.json",
        "**/*.toml",
        "**/*.md",
    ]

    # Dossiers à ignorer
    ignore_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        "deployment_packages",
    }

    for pattern in file_patterns:
        for filepath in repo_root.rglob(pattern):
            # Ignorer les dossiers spécifiques
            if any(ignore_dir in filepath.parts for ignore_dir in ignore_dirs):
                continue

            secrets = extract_secrets_from_file(filepath)
            for secret in secrets:
<<<<<<< HEAD
                used_secrets[secret].append(str(filepath.relative_to(repo_root)))
=======
                used_secrets[secret].append(
                    str(filepath.relative_to(repo_root))
                )
>>>>>>> origin/main

    return used_secrets


def main():
    """Fonction principale de validation."""
    print("🔍 Validation de la cohérence des secrets d'environnement\n")

    # Charger les secrets déclarés
    declared_secrets = load_declared_secrets()
    print(f"📋 Secrets déclarés ({len(declared_secrets)}):")
    for secret in sorted(declared_secrets):
        print(f"  ✅ {secret}")
    print()

    # Scanner le repository
    used_secrets = scan_repository()
    print(f"🔎 Secrets utilisés dans le code ({len(used_secrets)}):")
    for secret in sorted(used_secrets.keys()):
        print(f"  📄 {secret}")
    print()

    # Vérifier la cohérence
    missing_declarations = used_secrets.keys() - declared_secrets
    unused_declarations = declared_secrets - used_secrets.keys()

    # Rapport des incohérences
    if missing_declarations:
        print("❌ Secrets utilisés mais non déclarés:")
        for secret in sorted(missing_declarations):
            print(f"  🚨 {secret}")
            print(f"     Utilisé dans: {', '.join(used_secrets[secret][:3])}")
            if len(used_secrets[secret]) > 3:
<<<<<<< HEAD
                print(f"     ... et {len(used_secrets[secret]) - 3} autres fichiers")
=======
                print(
                    f"     ... et {len(used_secrets[secret]) - 3} autres fichiers"
                )
>>>>>>> origin/main
        print()

    if unused_declarations:
        print("⚠️  Secrets déclarés mais non utilisés:")
        for secret in sorted(unused_declarations):
            print(f"  🔸 {secret}")
        print()

    # Résumé
    if not missing_declarations and not unused_declarations:
        print("✅ Tous les secrets sont cohérents!")
        return 0
    else:
        print("📊 Résumé:")
<<<<<<< HEAD
        print(f"  - Secrets cohérents: {len(declared_secrets & used_secrets.keys())}")
=======
        print(
            f"  - Secrets cohérents: {len(declared_secrets & used_secrets.keys())}"
        )
>>>>>>> origin/main
        print(f"  - Manquent déclarations: {len(missing_declarations)}")
        print(f"  - Déclarations inutilisées: {len(unused_declarations)}")
        return 1


if __name__ == "__main__":
    exit(main())
