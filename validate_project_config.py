#!/usr/bin/env python3
"""
Script de validation pour s'assurer que tous les fichiers utilisent SUPABASE_PROJECT_ID
au lieu de SUPABASE_PROJECT_REF
"""

import os
import re
from pathlib import Path


def check_file_for_project_ref(file_path: Path) -> dict:
    """Vérifie un fichier pour les références incorrectes."""
    if not file_path.exists():
        return {"file": str(file_path), "exists": False}

    content = file_path.read_text()

    # Recherche les anciennes références
    old_refs = re.findall(r"SUPABASE_PROJECT_REF", content)
    new_refs = re.findall(r"SUPABASE_PROJECT_ID", content)

    return {
        "file": str(file_path),
        "exists": True,
        "old_refs": len(old_refs),
        "new_refs": len(new_refs),
        "lines_with_old": [
            f"L{i+1}: {line.strip()}"
            for i, line in enumerate(content.split("\n"))
            if "SUPABASE_PROJECT_REF" in line
        ],
    }


def main():
    """Fonction principale de validation."""
    print("🔍 Validation de la configuration SUPABASE_PROJECT_ID")
    print(
        "📋 Vérification que tous les fichiers utilisent PROJECT_ID au lieu de PROJECT_REF"
    )
    print("-" * 70)

    # Fichiers à vérifier
    files_to_check = [
        ".github/workflows/deploy-dashboard.yml",
        "deploy-supabase.sh",
        "DASHBOARD_CLOUD.md",
        "supabase/config.toml",
    ]

    all_good = True

    for file_path in files_to_check:
        full_path = Path(file_path)
        result = check_file_for_project_ref(full_path)

        if not result["exists"]:
            print(f"⚠️  {file_path} - Fichier non trouvé")
            continue

        if result["old_refs"] > 0:
            print(
                f"❌ {file_path} - {result['old_refs']} référence(s) à PROJECT_REF trouvée(s)"
            )
            for line in result["lines_with_old"]:
                print(f"   {line}")
            all_good = False
        else:
            print(f"✅ {file_path} - Aucune référence à PROJECT_REF")

        if result["new_refs"] > 0:
            print(f"   ✅ {result['new_refs']} référence(s) à PROJECT_ID trouvée(s)")

        print()

    # Résumé final
    print("-" * 70)
    if all_good:
        print("🎉 Configuration PROJECT_ID validée avec succès!")
        print("✅ Tous les fichiers utilisent SUPABASE_PROJECT_ID")
    else:
        print("❌ Problèmes détectés - certains fichiers utilisent encore PROJECT_REF")
        print("🔧 Remplacez toutes les occurrences de PROJECT_REF par PROJECT_ID")

    print("\n📋 Variables d'environnement requises:")
    print("- SUPABASE_ACCESS_TOKEN: Token d'accès Supabase")
    print("- SUPABASE_PROJECT_ID: ID du projet Supabase (pas REF)")
    print("- SPB_EDGE_FUNCTIONS: dHx8o@3?G4!QT86C")

    return 0 if all_good else 1


if __name__ == "__main__":
    exit(main())
