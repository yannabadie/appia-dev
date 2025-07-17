#!/bin/bash
# Test rapide de l'orchestrateur après correction Supabase

echo "🔧 Test de l'orchestrateur JARVYS après correction Supabase..."

# Test de l'environnement
echo "📊 Vérification de l'environnement..."
python3 -c "
import os
from supabase import create_client, Client

# Test Supabase
try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        
        # Test des tables
        tables_to_test = ['jarvys_memory', 'orchestrator_logs', 'code_validations']
        for table in tables_to_test:
            try:
                result = supabase.table(table).select('count').execute()
                print(f'✅ Table {table}: Accessible')
            except Exception as e:
                print(f'❌ Table {table}: Erreur - {e}')
        
        print('✅ Supabase: Connexion réussie')
    else:
        print('⚠️ Supabase: Variables d''environnement manquantes')
except Exception as e:
    print(f'❌ Supabase: Erreur - {e}')
"

echo ""
echo "🚀 Test de l'orchestrateur en mode single cycle..."
JARVYS_SINGLE_CYCLE=true python3 grok_orchestrator.py

echo ""
echo "📋 Test terminé. Vérifiez les résultats ci-dessus."
