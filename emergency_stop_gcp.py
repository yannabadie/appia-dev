#!/usr/bin/env python3
"""
🚨 Emergency Stop pour Orchestrateur GCP
=======================================

Script d'urgence pour arrêter l'orchestrateur GCP et reprendre le contrôle manuel.
Utilise l'API GitHub et Supabase pour signaler l'arrêt d'urgence.
"""

import os
from datetime import datetime

import requests

from supabase import create_client


def emergency_stop():
    """Arrête l'orchestrateur GCP et active le mode manuel"""

    print("🚨 ARRÊT D'URGENCE DE L'ORCHESTRATEUR GCP")
    print("=" * 50)

    # 1. Signaler l'arrêt via Supabase
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)

            # Insérer signal d'arrêt d'urgence
            emergency_signal = {
                "type": "EMERGENCY_STOP",
                "timestamp": datetime.now().isoformat(),
                "source": "codespace_manual",
                "message": "Arrêt d'urgence demandé par l'utilisateur",
                "status": "active",
            }

            supabase.table("orchestrator_control").insert(emergency_signal).execute()
            print("✅ Signal d'arrêt envoyé via Supabase")

    except Exception as e:
        print(f"⚠️  Erreur Supabase: {e}")

    # 2. Créer un verrou GitHub pour bloquer l'orchestrateur
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            # Créer un fichier de verrou dans le repo
            lock_content = {
                "emergency_stop": True,
                "timestamp": datetime.now().isoformat(),
                "reason": "Manual intervention required",
                "initiated_by": "codespace_user",
            }

            # Via GitHub API
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            # Créer/modifier le fichier de verrou
            import base64
            import json

            lock_data = {
                "message": "🚨 Emergency stop - Manual intervention",
                "content": base64.b64encode(
                    json.dumps(lock_content, indent=2).encode()
                ).decode(),
                "branch": "grok-evolution",
            }

            response = requests.put(
                "https://api.github.com/repos/yannabadie/appia-dev/contents/.emergency_lock",
                headers=headers,
                json=lock_data,
            )

            if response.status_code in [200, 201]:
                print("✅ Verrou d'urgence créé sur GitHub")
            else:
                print(f"⚠️  Erreur GitHub API: {response.status_code}")

    except Exception as e:
        print(f"⚠️  Erreur GitHub: {e}")

    # 3. Instructions pour l'utilisateur
    print("\n🎯 CONTRÔLE MANUEL ACTIVÉ")
    print("=" * 30)
    print("✅ L'orchestrateur GCP va détecter le signal d'arrêt")
    print("✅ Toutes les modifications automatiques sont suspendues")
    print("✅ Vous pouvez maintenant modifier GitHub manuellement")
    print("\n📋 Pour reprendre l'orchestrateur plus tard :")
    print("   python3 emergency_resume_gcp.py")
    print("\n⚠️  L'orchestrateur va vérifier le verrou toutes les 5 minutes")


def check_gcp_status():
    """Vérifie si l'orchestrateur GCP est actif"""
    try:
        # Vérifier via Supabase s'il y a une activité récente
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)

            # Chercher la dernière activité
            result = (
                supabase.table("orchestrator_logs")
                .select("*")
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                last_activity = result.data[0]
                print(f"📊 Dernière activité GCP: {last_activity.get('timestamp')}")
                print(f"📝 Type: {last_activity.get('action')}")
                return True
            else:
                print("📊 Aucune activité GCP récente détectée")
                return False

    except Exception as e:
        print(f"⚠️  Impossible de vérifier le statut GCP: {e}")
        return None


if __name__ == "__main__":
    print("🔍 Vérification du statut GCP...")
    gcp_active = check_gcp_status()

    if gcp_active:
        confirm = input(
            "\n⚠️  L'orchestrateur GCP semble actif. Confirmer l'arrêt d'urgence ? (y/N): "
        )
        if confirm.lower() in ["y", "yes", "oui"]:
            emergency_stop()
        else:
            print("❌ Arrêt d'urgence annulé")
    else:
        print("✅ L'orchestrateur GCP ne semble pas actif")
        emergency_stop()
