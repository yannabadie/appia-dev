-- DIAGNOSTIC SUPABASE - Vérification de l'état actuel
-- Exécutez ce script AVANT le script de correction

-- ==============================================
-- DIAGNOSTIC 1: Vérifier les tables existantes
-- ==============================================

SELECT 
    schemaname,
    tablename,
    tableowner,
    hasindexes,
    hasrules,
    hastriggers
FROM pg_tables 
WHERE schemaname = 'public' 
AND (tablename LIKE '%jarvys%' OR tablename LIKE '%orchestrator%' OR tablename LIKE '%validation%')
ORDER BY tablename;

-- ==============================================
-- DIAGNOSTIC 2: Vérifier les colonnes des tables existantes
-- ==============================================

-- Si la table jarvys_memory existe
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jarvys_memory') THEN
        RAISE NOTICE 'Table jarvys_memory existe - vérification des colonnes:';
    ELSE
        RAISE NOTICE 'Table jarvys_memory n''existe pas';
    END IF;
END $$;

-- Afficher les colonnes de jarvys_memory si elle existe
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'jarvys_memory' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- ==============================================
-- DIAGNOSTIC 3: Vérifier les index existants
-- ==============================================

SELECT 
    indexname,
    tablename,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
AND (tablename LIKE '%jarvys%' OR tablename LIKE '%orchestrator%' OR tablename LIKE '%validation%')
ORDER BY tablename, indexname;

-- ==============================================
-- DIAGNOSTIC 4: Vérifier les policies RLS
-- ==============================================

SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies 
WHERE schemaname = 'public' 
AND (tablename LIKE '%jarvys%' OR tablename LIKE '%orchestrator%' OR tablename LIKE '%validation%')
ORDER BY tablename, policyname;

-- ==============================================
-- DIAGNOSTIC 5: Vérifier les contraintes
-- ==============================================

SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_schema = 'public'
AND (tc.table_name LIKE '%jarvys%' OR tc.table_name LIKE '%orchestrator%' OR tc.table_name LIKE '%validation%')
ORDER BY tc.table_name, tc.constraint_name;

-- ==============================================
-- RÉSUMÉ DU DIAGNOSTIC
-- ==============================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND (table_name LIKE '%jarvys%' OR table_name LIKE '%orchestrator%' OR table_name LIKE '%validation%');
    
    RAISE NOTICE '===============================================';
    RAISE NOTICE 'DIAGNOSTIC SUPABASE ORCHESTRATEUR JARVYS';
    RAISE NOTICE '===============================================';
    RAISE NOTICE 'Tables trouvées: %', table_count;
    
    IF table_count = 0 THEN
        RAISE NOTICE '❌ Aucune table d''orchestrateur trouvée';
        RAISE NOTICE '➡️ Vous pouvez exécuter directement fix_supabase_schema.sql';
    ELSE
        RAISE NOTICE '⚠️ Tables existantes détectées';
        RAISE NOTICE '➡️ Vérifiez les détails ci-dessus avant d''exécuter fix_supabase_schema.sql';
    END IF;
    
    RAISE NOTICE '===============================================';
END $$;
