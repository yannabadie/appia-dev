#!/usr/bin/env python3
"""
🔄 Emergency Resume pour Orchestrateur GCP
==========================================

Script pour reprendre l'orchestrateur GCP après un arrêt d'urgence.
"""

import os
from datetime import datetime

import requests

from supabase import create_client


def emergency_resume():
    """Reprend l'orchestrateur GCP après arrêt d'urgence"""

    print("🔄 REPRISE DE L'ORCHESTRATEUR GCP")
    print("=" * 40)

    # 1. Supprimer le signal d'arrêt via Supabase
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)

            # Marquer l'arrêt d'urgence comme résolu
            resume_signal = {
                "type": "EMERGENCY_RESUME",
                "timestamp": datetime.now().isoformat(),
                "source": "codespace_manual",
                "message": "Reprise autorisée par l'utilisateur",
                "status": "active",
            }

            supabase.table("orchestrator_control").insert(resume_signal).execute()
            print("✅ Signal de reprise envoyé via Supabase")

    except Exception as e:
        print(f"⚠️  Erreur Supabase: {e}")

    # 2. Supprimer le verrou GitHub
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            # Supprimer le fichier de verrou
            response = requests.delete(
                "https://api.github.com/repos/yannabadie/appia-dev/contents/.emergency_lock",
                headers=headers,
                json={
                    "message": "🔄 Emergency resume - Orchestrator reactivated",
                    "branch": "grok-evolution",
                },
            )

            if response.status_code == 200:
                print("✅ Verrou d'urgence supprimé de GitHub")
            else:
                print(f"⚠️  Erreur suppression verrou: {response.status_code}")

    except Exception as e:
        print(f"⚠️  Erreur GitHub: {e}")

    print("\n🎯 ORCHESTRATEUR GCP RÉACTIVÉ")
    print("=" * 35)
    print("✅ L'orchestrateur va reprendre ses activités automatiques")
    print("✅ Synchronisation GitHub réactivée")
    print("✅ Monitoring en temps réel restauré")


if __name__ == "__main__":
    confirm = input("🔄 Confirmer la reprise de l'orchestrateur GCP ? (y/N): ")
    if confirm.lower() in ["y", "yes", "oui"]:
        emergency_resume()
    else:
        print("❌ Reprise annulée")
