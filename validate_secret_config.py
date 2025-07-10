#!/usr/bin/env python3
"""
Script de validation de la configuration du secret SPB_EDGE_FUNCTIONS
Vérifie que la valeur est correctement configurée dans tous les fichiers.
"""

import os
import re
from pathlib import Path

SECRET_VALUE = "dHx8o@3?G4!QT86C"
SECRET_NAME = "SPB_EDGE_FUNCTIONS"


def check_file_for_secret(file_path: Path, content: str) -> dict:
    """Vérifie un fichier pour la présence du secret."""
    results = {
        "file": str(file_path),
        "secret_found": False,
        "correct_value": False,
        "occurrences": [],
    }

    # Recherche toutes les occurrences du nom du secret
    secret_pattern = re.compile(rf"{SECRET_NAME}", re.IGNORECASE)
    matches = list(secret_pattern.finditer(content))

    if matches:
        results["secret_found"] = True

        # Recherche la valeur spécifique
        value_pattern = re.compile(rf"{re.escape(SECRET_VALUE)}")
        value_matches = list(value_pattern.finditer(content))

        if value_matches:
            results["correct_value"] = True

        # Récupère les lignes contenant le secret
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if SECRET_NAME in line:
                results["occurrences"].append(
                    {"line_number": i + 1, "line_content": line.strip()}
                )

    return results


def main():
    """Fonction principale de validation."""
    print(f"🔍 Validation de la configuration du secret {SECRET_NAME}")
    print(f"🔑 Valeur attendue: {SECRET_VALUE}")
    print("-" * 60)

    # Fichiers à vérifier
    files_to_check = [
        "supabase/functions/jarvys-dashboard/index.ts",
        "DASHBOARD_CLOUD.md",
        ".github/workflows/deploy-dashboard.yml",
        "deploy-supabase.sh",
    ]

    all_good = True

    for file_path in files_to_check:
        full_path = Path(file_path)

        if not full_path.exists():
            print(f"❌ {file_path} - Fichier non trouvé")
            all_good = False
            continue

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        result = check_file_for_secret(full_path, content)

        if result["secret_found"]:
            if result["correct_value"]:
                print(f"✅ {file_path} - Secret configuré correctement")
            else:
                print(f"⚠️  {file_path} - Secret trouvé mais valeur différente")
                all_good = False
        else:
            print(f"ℹ️  {file_path} - Aucune référence au secret trouvée")

        # Affiche les occurrences
        for occ in result["occurrences"]:
            print(f"   L{occ['line_number']:3d}: {occ['line_content']}")

        print()

    # Résumé final
    print("-" * 60)
    if all_good:
        print("🎉 Configuration du secret validée avec succès!")
        print(f"✅ Le secret {SECRET_NAME} est correctement configuré")
        print(f"🔑 Valeur: {SECRET_VALUE}")
    else:
        print("❌ Problèmes détectés dans la configuration")
        print("🔧 Vérifiez les fichiers marqués en erreur")

    # Instructions de déploiement
    print("\n📋 Instructions de déploiement:")
    print("1. 🔑 Configurez le secret dans GitHub:")
    print(f"   Repository Settings > Secrets > {SECRET_NAME} = {SECRET_VALUE}")
    print("2. 🌐 Configurez dans Supabase:")
    print(f'   supabase secrets set {SECRET_NAME}="{SECRET_VALUE}"')
    print("3. 🚀 Déployez le dashboard:")
    print("   git push origin main  # Déclenche le déploiement automatique")


if __name__ == "__main__":
    main()
