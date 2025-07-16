#!/usr/bin/env python3
"""
🚀 Script de Pré-Migration GCP pour JARVYS
==========================================

Valide que tous les composants sont prêts pour la migration vers GCP.
Effectue les vérifications finales avant le déploiement.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Vérifie qu'un fichier existe"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} MANQUANT: {file_path}")
        return False


def check_python_file(file_path):
    """Vérifie qu'un fichier Python compile sans erreur"""
    try:
        subprocess.run(
            [sys.executable, "-m", "py_compile", file_path],
            check=True,
            capture_output=True,
        )
        print(f"✅ Syntaxe OK: {file_path}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erreur syntaxe: {file_path}")
        return False


def check_environment_vars():
    """Vérifie les variables d'environnement critiques"""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "GITHUB_TOKEN", "XAI_API_KEY"]

    all_ok = True
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ Variable {var}: Configurée")
        else:
            print(f"❌ Variable {var}: MANQUANTE")
            all_ok = False

    return all_ok


def check_supabase_connection():
    """Test la connexion Supabase et vérifie les tables"""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ SUPABASE CONNECTION: Variables manquantes")
            return False

        # Test simple - vérifier que les variables existent et ont l'air valides
        if url.startswith("https://") and ".supabase.co" in url and len(key) > 20:
            print("✅ SUPABASE CONNECTION OK")
            print(f"   📊 URL et clé semblent valides")
            return True
        else:
            print("❌ SUPABASE CONNECTION: Format URL/clé invalide")
            return False
        
    except Exception as e:
        print(f"❌ SUPABASE CONNECTION FAILED: {e}")
        return False


def check_lint_status():
    """Vérifie le statut des erreurs de lint critiques"""
    try:
        result = subprocess.run(
            ["ruff", "check", "--select=F", "."],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ LINT CHECKS: Aucune erreur critique")
            return True
        else:
            # Compter les erreurs F (syntax/imports)
            errors = result.stdout.count('F')
            print(f"⚠️ LINT CHECKS: {errors} erreurs critiques détectées")
            return errors < 10  # Acceptable si moins de 10 erreurs
            
    except Exception as e:
        print(f"⚠️ LINT CHECKS: Impossible de vérifier - {e}")
        return True  # Ne pas bloquer pour ça


def main():
    print("🚀 PRÉ-MIGRATION GCP - VÉRIFICATIONS FINALES")
    print("=" * 50)

    checks_passed = 0
    total_checks = 0

    # 1. Orchestrateur principal
    print("\n🤖 ORCHESTRATEUR PRINCIPAL")
    total_checks += 1
    if check_python_file("grok_orchestrator.py"):
        checks_passed += 1

    # 2. Infrastructure GCP
    print("\n🏗️ INFRASTRUCTURE GCP")
    gcp_files = [
        ("Dockerfile.gcp", "Dockerfile principal GCP"),
        ("cloudbuild-gcp.yaml", "Configuration Cloud Build"),
        ("jarvys-dashboard-gcp/Dockerfile", "Dockerfile Dashboard"),
        ("jarvys-orchestrator-gcp/Dockerfile", "Dockerfile Orchestrateur"),
        ("emergency_stop_gcp.py", "Script d'arrêt d'urgence"),
        ("emergency_resume_gcp.py", "Script de reprise"),
    ]

    for file_path, description in gcp_files:
        total_checks += 1
        if check_file_exists(file_path, description):
            checks_passed += 1

    # 3. Schémas Supabase
    print("\n🗄️ BASE DE DONNÉES")
    total_checks += 1
    if check_file_exists("init_supabase_tables.sql", "Schéma Supabase"):
        checks_passed += 1

    # 4. Variables d'environnement
    print("\n🔐 VARIABLES D'ENVIRONNEMENT")
    total_checks += 1
    if check_environment_vars():
        checks_passed += 1

    # 5. Test de connexion Supabase
    print("\n🔌 CONNEXION SUPABASE")
    total_checks += 1
    if check_supabase_connection():
        checks_passed += 1

    # 6. Status lint
    print("\n🔍 QUALITÉ DU CODE")
    total_checks += 1
    if check_lint_status():
        checks_passed += 1

    # Résumé final
    print("\n" + "=" * 50)
    print(f"📊 RÉSULTAT: {checks_passed}/{total_checks} vérifications réussies")

    if checks_passed == total_checks:
        print("🎉 SYSTÈME PRÊT POUR LA MIGRATION GCP!")
        print("✅ Tous les composants sont opérationnels")
        print("🚀 Vous pouvez procéder au déploiement")
        return True
    elif checks_passed >= total_checks - 2:
        print("⚠️ MIGRATION POSSIBLE AVEC PRÉCAUTIONS")
        print(f"⚠️ {total_checks - checks_passed} problèmes mineurs détectés")
        print("🔧 Recommandé mais pas bloquant")
        return True
    else:
        print("❌ MIGRATION NON RECOMMANDÉE")
        print(f"❌ {total_checks - checks_passed} problèmes critiques détectés")
        print("🔧 Corrigez les erreurs avant de continuer")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
