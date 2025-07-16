#!/usr/bin/env python3
"""
🔧 Création manuelle des tables Supabase via API REST
====================================================

Alternative pour créer les tables JARVYS quand l'API RPC n'est pas disponible.
"""

import json
import os
from datetime import datetime

import requests


def create_tables_via_api():
    """Crée les tables via l'API REST de Supabase"""

    print("🔧 CRÉATION TABLES VIA API REST SUPABASE")
    print("=" * 42)

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Variables d'environnement manquantes")
        return False

    # Headers pour l'API Supabase
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    # URL de base pour l'API REST
    rest_url = f"{supabase_url}/rest/v1"

    print(f"🔗 URL Supabase: {supabase_url}")
    print(
        f"🔑 Clé API: {'***' + supabase_key[-10:] if len(supabase_key) > 10 else '***'}"
    )

    # Test de connexion simple
    try:
        response = requests.get(f"{rest_url}/", headers=headers, timeout=10)
        print(f"✅ Connexion API: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

    # Créer une première table simple pour tester
    try:
        print("\n📝 Instructions pour créer les tables manuellement:")
        print("1. Allez sur https://supabase.com/dashboard")
        print("2. Sélectionnez votre projet")
        print("3. Allez dans 'SQL Editor'")
        print("4. Copiez-collez le contenu du fichier init_supabase_tables.sql")
        print("5. Exécutez le script SQL")

        # Essayer de créer directement une table simple via insertion
        print("\n🔄 Tentative de création table jarvys_memory...")

        # Données d'exemple pour forcer la création de structure
        test_data = {
            "content": "Test initialisation JARVYS",
            "agent_source": "JARVYS_DEV",
            "memory_type": "system",
            "user_context": "test",
            "importance_score": 1.0,
            "tags": ["test"],
            "metadata": {"init": True},
        }

        response = requests.post(
            f"{rest_url}/jarvys_memory", headers=headers, json=test_data, timeout=10
        )

        if response.status_code in [200, 201]:
            print("✅ Table jarvys_memory existe déjà ou créée")
            return True
        else:
            print(f"❌ Table jarvys_memory n'existe pas: {response.status_code}")
            print(f"Réponse: {response.text[:200]}...")

    except Exception as e:
        print(f"❌ Erreur test table: {e}")

    return False


def create_minimal_setup():
    """Crée un setup minimal pour JARVYS sans tables complètes"""

    print("\n🔄 SETUP MINIMAL SANS TABLES")
    print("=" * 35)

    try:
        # Créer un fichier local de configuration
        config = {
            "jarvys_setup": {
                "status": "minimal",
                "timestamp": datetime.now().isoformat(),
                "tables_status": "manual_creation_required",
                "next_steps": [
                    "Créer les tables manuellement via Supabase Dashboard",
                    "Exécuter le script init_supabase_tables.sql",
                    "Tester la connexion avec test_supabase_connection.py",
                ],
            }
        }

        with open("jarvys_setup_status.json", "w") as f:
            json.dump(config, f, indent=2)

        print("✅ Configuration minimale créée: jarvys_setup_status.json")

        # Créer un script de test simple
        test_script = '''#!/usr/bin/env python3
"""Test de connexion Supabase pour JARVYS"""

import os
from supabase import create_client

def test_connection():
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE")
        
        if not supabase_url or not supabase_key:
            print("❌ Variables d'environnement manquantes")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Test simple
        result = supabase.table("jarvys_memory").select("count", count="exact").execute()
        print(f"✅ Table jarvys_memory: {result.count} entrées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_connection()
'''

        with open("test_supabase_connection.py", "w") as f:
            f.write(test_script)

        print("✅ Script de test créé: test_supabase_connection.py")
        return True

    except Exception as e:
        print(f"❌ Erreur setup minimal: {e}")
        return False


if __name__ == "__main__":
    success = create_tables_via_api()

    if not success:
        print("\n🔄 Basculement vers setup minimal...")
        create_minimal_setup()

        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. Aller sur votre dashboard Supabase")
        print("2. SQL Editor → Nouveau query")
        print("3. Copier le contenu de init_supabase_tables.sql")
        print("4. Exécuter le script")
        print("5. Tester avec: python3 test_supabase_connection.py")
        print("\n💡 Les tables JARVYS seront alors opérationnelles !")
