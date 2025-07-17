#!/usr/bin/env python3
"""
🔧 Initialisation automatique des tables Supabase pour JARVYS
=============================================================

Script pour créer automatiquement toutes les tables nécessaires
à l'écosystème JARVYS dans Supabase.

Usage:
    python3 init_supabase_jarvys.py

Pré-requis:
    - SUPABASE_URL et SUPABASE_KEY dans les variables d'environnement
    - Permissions de création de tables (service_role key recommandée)
"""

import os
import sys
from datetime import datetime

from supabase import create_client


def init_supabase_tables():
    """Initialise toutes les tables nécessaires pour JARVYS"""

    print("🔧 INITIALISATION BASE DE DONNÉES JARVYS")
    print("=" * 45)

    # Vérifier les variables d'environnement
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE")

    if not supabase_url or not supabase_key:
        print("❌ ERREUR: Variables d'environnement manquantes")
        print("   SUPABASE_URL =", supabase_url)
        print("   SUPABASE_KEY =", "***" if supabase_key else "MANQUANT")
        return False

    try:
        # Créer le client Supabase
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connexion Supabase établie")

        # Définir les requêtes SQL de création
        tables_sql = [
            # 1. Table mémoire infinie JARVYS
            """
            CREATE TABLE IF NOT EXISTS public.jarvys_memory (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                content TEXT NOT NULL,
                agent_source VARCHAR(50) NOT NULL DEFAULT 'JARVYS_DEV',
                memory_type VARCHAR(50) NOT NULL DEFAULT 'experience',
                user_context VARCHAR(100) NOT NULL DEFAULT 'default',
                importance_score FLOAT NOT NULL DEFAULT 0.5 CHECK (importance_score >= 0 AND importance_score <= 1),
                tags TEXT[] DEFAULT '{}',
                metadata JSONB DEFAULT '{}',
                embedding VECTOR(1536),
                similarity FLOAT DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            # 2. Table logs orchestrateur
            """
            CREATE TABLE IF NOT EXISTS public.orchestrator_logs (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                agent_type VARCHAR(50) NOT NULL,
                action VARCHAR(100) NOT NULL,
                task TEXT,
                repo VARCHAR(50),
                status VARCHAR(50),
                metadata JSONB DEFAULT '{}',
                error_details TEXT,
                success BOOLEAN DEFAULT true
            );
            """,
            # 3. Table métriques JARVYS
            """
            CREATE TABLE IF NOT EXISTS public.jarvys_metrics (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                agent_type VARCHAR(50) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                service VARCHAR(50),
                success BOOLEAN NOT NULL,
                metadata JSONB DEFAULT '{}',
                user_context VARCHAR(100) DEFAULT 'default',
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            # 4. Table contrôle d'urgence
            """
            CREATE TABLE IF NOT EXISTS public.orchestrator_control (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                source VARCHAR(50) NOT NULL,
                message TEXT,
                status VARCHAR(20) DEFAULT 'active',
                metadata JSONB DEFAULT '{}'
            );
            """,
            # 5. Table suggestions
            """
            CREATE TABLE IF NOT EXISTS public.orchestrator_suggestions (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 5),
                status VARCHAR(20) DEFAULT 'pending',
                created_by VARCHAR(50) DEFAULT 'JARVYS_DEV',
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            # 6. Table validations de tâches
            """
            CREATE TABLE IF NOT EXISTS public.task_validations (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                task_id VARCHAR(100) NOT NULL,
                action VARCHAR(20) NOT NULL,
                priority INTEGER DEFAULT 3,
                comment TEXT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                validator VARCHAR(50) NOT NULL
            );
            """,
            # 7. Table priorités de tâches
            """
            CREATE TABLE IF NOT EXISTS public.task_priorities (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                task_id VARCHAR(100) NOT NULL UNIQUE,
                priority INTEGER NOT NULL CHECK (priority >= 1 AND priority <= 5),
                notes TEXT,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            # 8. Table chat orchestrateur
            """
            CREATE TABLE IF NOT EXISTS public.orchestrator_chat (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                message TEXT NOT NULL,
                sender VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                type VARCHAR(50) DEFAULT 'user_to_orchestrator',
                status VARCHAR(20) DEFAULT 'pending',
                metadata JSONB DEFAULT '{}'
            );
            """,
            # 9. Table logs générique (compatibilité)
            """
            CREATE TABLE IF NOT EXISTS public.logs (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                task TEXT,
                repo VARCHAR(50),
                status VARCHAR(50),
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                lint_output TEXT,
                test_result TEXT,
                doc_update TEXT,
                pr_url TEXT,
                reflection TEXT,
                adapt_fix TEXT,
                file_error TEXT,
                metadata JSONB DEFAULT '{}'
            );
            """,
        ]

        # Créer les tables une par une
        tables_created = 0
        for i, sql in enumerate(tables_sql, 1):
            try:
                result = supabase.rpc("exec_sql", {"sql": sql}).execute()
                table_name = sql.split("public.")[1].split("(")[0].strip()
                print(f"✅ Table {i}/9: {table_name}")
                tables_created += 1
            except Exception as e:
                print(f"⚠️  Erreur table {i}: {str(e)[:100]}...")
                # Continuer avec les autres tables

        # Créer les index pour la performance
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_jarvys_memory_user_context ON public.jarvys_memory(user_context);",
            "CREATE INDEX IF NOT EXISTS idx_jarvys_memory_agent_source ON public.jarvys_memory(agent_source);",
            "CREATE INDEX IF NOT EXISTS idx_jarvys_memory_memory_type ON public.jarvys_memory(memory_type);",
            "CREATE INDEX IF NOT EXISTS idx_jarvys_memory_importance ON public.jarvys_memory(importance_score DESC);",
            "CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_timestamp ON public.orchestrator_logs(timestamp DESC);",
            "CREATE INDEX IF NOT EXISTS idx_jarvys_metrics_timestamp ON public.jarvys_metrics(timestamp DESC);",
        ]

        indexes_created = 0
        for sql in indexes_sql:
            try:
                supabase.rpc("exec_sql", {"sql": sql}).execute()
                indexes_created += 1
            except Exception as e:
                print(f"⚠️  Index warning: {str(e)[:50]}...")

        print(f"✅ Index créés: {indexes_created}/{len(indexes_sql)}")

        # Insérer des données de test
        try:
            init_data = {
                "content": f"Initialisation JARVYS Database - {datetime.now().isoformat()}",
                "agent_source": "JARVYS_DEV",
                "memory_type": "system",
                "user_context": "initialization",
                "importance_score": 1.0,
                "tags": ["system", "initialization", "database"],
                "metadata": {
                    "version": "1.0",
                    "setup_date": datetime.now().isoformat(),
                    "tables_created": tables_created,
                },
            }

            result = supabase.table("jarvys_memory").insert(init_data).execute()
            print("✅ Données de test insérées")

        except Exception as e:
            print(f"⚠️  Données de test: {str(e)[:100]}...")

        print("\n🎉 INITIALISATION TERMINÉE")
        print(f"📊 Tables créées: {tables_created}/9")
        print(f"📈 Index créés: {indexes_created}")
        print("🔗 Accédez à votre dashboard Supabase pour vérifier")

        return True

    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {str(e)}")
        return False


def test_connection():
    """Test la connexion et les tables créées"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE")

        supabase = create_client(supabase_url, supabase_key)

        # Tester la table jarvys_memory
        result = (
            supabase.table("jarvys_memory").select("count", count="exact").execute()
        )
        memory_count = result.count

        print("\n🧪 TEST DE CONNEXION:")
        print(f"✅ Table jarvys_memory: {memory_count} entrées")

        # Tester les autres tables principales
        for table in ["orchestrator_logs", "jarvys_metrics", "orchestrator_control"]:
            try:
                result = supabase.table(table).select("count", count="exact").execute()
                print(f"✅ Table {table}: {result.count} entrées")
            except Exception as e:
                print(f"❌ Table {table}: erreur - {str(e)[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Test de connexion échoué: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Démarrage initialisation Supabase JARVYS...")

    # Initialiser les tables
    success = init_supabase_tables()

    if success:
        # Tester la connexion
        test_connection()
        print(
            "\n✅ Initialisation réussie ! Vous pouvez maintenant utiliser la mémoire JARVYS."
        )
    else:
        print("\n❌ Initialisation échouée. Vérifiez vos variables d'environnement.")
        sys.exit(1)
