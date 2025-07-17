#!/usr/bin/env python3
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
        result = (
            supabase.table("jarvys_memory").select("count", count="exact").execute()
        )
        print(f"✅ Table jarvys_memory: {result.count} entrées")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    test_connection()
