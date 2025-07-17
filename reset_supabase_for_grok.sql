-- 🗑️ RESET COMPLETE SUPABASE SCHEMA FOR GROK ORCHESTRATOR
-- =========================================================
-- 
-- ATTENTION: Ce script supprime TOUTES les données existantes
-- et recrée la structure optimisée pour grok_orchestrator.py
--
-- À exécuter dans l'éditeur SQL de Supabase Dashboard

-- 1. SUPPRESSION COMPLÈTE DES TABLES EXISTANTES
-- =============================================

-- Supprimer toutes les politiques RLS existantes
DROP POLICY IF EXISTS "Enable all operations for service role" ON public.jarvys_memory;
DROP POLICY IF EXISTS "Enable all operations for service role" ON public.orchestrator_logs;
DROP POLICY IF EXISTS "Enable all operations for service role" ON public.logs;
DROP POLICY IF EXISTS "Allow JARVYS access" ON public.jarvys_memory;

-- Supprimer les triggers existants
DROP TRIGGER IF EXISTS update_jarvys_memory_updated_at ON public.jarvys_memory;
DROP TRIGGER IF EXISTS update_orchestrator_suggestions_updated_at ON public.orchestrator_suggestions;
DROP TRIGGER IF EXISTS update_task_priorities_updated_at ON public.task_priorities;

-- Supprimer les fonctions existantes
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Supprimer toutes les tables JARVYS existantes (CASCADE pour supprimer les dépendances)
DROP TABLE IF EXISTS public.jarvys_memory CASCADE;
DROP TABLE IF EXISTS public.orchestrator_logs CASCADE;
DROP TABLE IF EXISTS public.logs CASCADE;
DROP TABLE IF EXISTS public.jarvys_metrics CASCADE;
DROP TABLE IF EXISTS public.orchestrator_control CASCADE;
DROP TABLE IF EXISTS public.orchestrator_suggestions CASCADE;
DROP TABLE IF EXISTS public.task_validations CASCADE;
DROP TABLE IF EXISTS public.task_priorities CASCADE;
DROP TABLE IF EXISTS public.orchestrator_chat CASCADE;

-- Supprimer les index s'ils existent encore
DROP INDEX IF EXISTS idx_jarvys_memory_user_context;
DROP INDEX IF EXISTS idx_jarvys_memory_agent_source;
DROP INDEX IF EXISTS idx_jarvys_memory_memory_type;
DROP INDEX IF EXISTS idx_jarvys_memory_importance;
DROP INDEX IF EXISTS idx_jarvys_memory_created_at;
DROP INDEX IF EXISTS idx_orchestrator_logs_timestamp;
DROP INDEX IF EXISTS idx_orchestrator_logs_agent_type;
DROP INDEX IF EXISTS idx_logs_timestamp;

-- 2. RECREATION DES TABLES OPTIMISÉES POUR GROK ORCHESTRATOR
-- ==========================================================

-- Table principale pour la mémoire infinie JARVYS (Schema optimisé pour grok_orchestrator.py)
CREATE TABLE public.jarvys_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,                              -- Contenu textuel (pas JSONB)
    agent_source VARCHAR(50) NOT NULL DEFAULT 'JARVYS_DEV',
    memory_type VARCHAR(50) NOT NULL DEFAULT 'experience',
    user_context VARCHAR(100) NOT NULL DEFAULT 'orchestrator',
    importance_score FLOAT NOT NULL DEFAULT 0.5 CHECK (importance_score >= 0 AND importance_score <= 1),
    tags TEXT[] DEFAULT '{}',                           -- Array de tags
    metadata JSONB DEFAULT '{}',                        -- Métadonnées flexibles
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table pour les logs d'orchestrateur (Structure exacte attendue par le code)
CREATE TABLE public.orchestrator_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    agent_type VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    task TEXT,
    repo VARCHAR(50),
    status VARCHAR(50) DEFAULT 'completed',
    metadata JSONB DEFAULT '{}',
    error_details TEXT,
    success BOOLEAN DEFAULT true
);

-- Table logs générique (Compatibilité avec le code existant)
CREATE TABLE public.logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task TEXT,
    repo VARCHAR(50),
    status VARCHAR(50) DEFAULT 'completed',
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

-- 3. INDEX DE PERFORMANCE
-- ======================

-- Index pour jarvys_memory
CREATE INDEX idx_jarvys_memory_user_context ON public.jarvys_memory(user_context);
CREATE INDEX idx_jarvys_memory_agent_source ON public.jarvys_memory(agent_source);
CREATE INDEX idx_jarvys_memory_memory_type ON public.jarvys_memory(memory_type);
CREATE INDEX idx_jarvys_memory_importance ON public.jarvys_memory(importance_score DESC);
CREATE INDEX idx_jarvys_memory_created_at ON public.jarvys_memory(created_at DESC);

-- Index pour orchestrator_logs
CREATE INDEX idx_orchestrator_logs_timestamp ON public.orchestrator_logs(timestamp DESC);
CREATE INDEX idx_orchestrator_logs_agent_type ON public.orchestrator_logs(agent_type);
CREATE INDEX idx_orchestrator_logs_action ON public.orchestrator_logs(action);

-- Index pour logs
CREATE INDEX idx_logs_timestamp ON public.logs(timestamp DESC);
CREATE INDEX idx_logs_status ON public.logs(status);

-- 4. TRIGGERS POUR MISE À JOUR AUTOMATIQUE
-- ========================================

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger pour jarvys_memory
CREATE TRIGGER update_jarvys_memory_updated_at 
    BEFORE UPDATE ON public.jarvys_memory 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5. PERMISSIONS ET SÉCURITÉ
-- ===========================

-- Accorder tous les droits au service_role (nécessaire pour l'orchestrateur)
GRANT ALL ON public.jarvys_memory TO service_role;
GRANT ALL ON public.orchestrator_logs TO service_role;
GRANT ALL ON public.logs TO service_role;

-- Accorder les droits à authenticated (utilisateurs connectés)
GRANT SELECT, INSERT, UPDATE ON public.jarvys_memory TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.orchestrator_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.logs TO authenticated;

-- 6. DONNÉES D'INITIALISATION
-- ===========================

-- Insérer une mémoire d'initialisation pour tester
INSERT INTO public.jarvys_memory (
    content, 
    agent_source, 
    memory_type, 
    user_context, 
    importance_score, 
    tags, 
    metadata
) VALUES (
    'Base de données JARVYS réinitialisée pour grok_orchestrator - Système opérationnel',
    'JARVYS_DEV',
    'system_reset',
    'orchestrator_initialization',
    1.0,
    ARRAY['reset', 'initialization', 'grok', 'orchestrator'],
    '{"reset_date": "2025-07-17", "version": "grok_orchestrator_v1", "status": "operational"}'::jsonb
);

-- Insérer un log d'initialisation
INSERT INTO public.orchestrator_logs (
    agent_type,
    action,
    task,
    status,
    metadata
) VALUES (
    'JARVYS_DEV',
    'database_reset',
    'Réinitialisation complète de la base de données Supabase pour grok_orchestrator',
    'completed',
    '{"tables_recreated": 3, "indexes_created": 8, "previous_data": "deleted"}'::jsonb
);

-- Insérer dans logs pour compatibilité
INSERT INTO public.logs (
    task,
    status,
    metadata
) VALUES (
    'Initialisation base de données grok_orchestrator',
    'completed',
    '{"action": "database_reset", "success": true}'::jsonb
);

-- 7. COMMENTAIRES ET DOCUMENTATION
-- ================================

COMMENT ON TABLE public.jarvys_memory IS 'Mémoire infinie JARVYS optimisée pour grok_orchestrator';
COMMENT ON TABLE public.orchestrator_logs IS 'Logs détaillés du grok_orchestrator autonome';
COMMENT ON TABLE public.logs IS 'Table logs générique pour compatibilité';

COMMENT ON COLUMN public.jarvys_memory.content IS 'Contenu textuel de la mémoire (TEXT)';
COMMENT ON COLUMN public.jarvys_memory.agent_source IS 'Source de l''agent (JARVYS_DEV, JARVYS_AI)';
COMMENT ON COLUMN public.jarvys_memory.user_context IS 'Contexte utilisateur (orchestrator, dashboard, etc.)';
COMMENT ON COLUMN public.jarvys_memory.importance_score IS 'Score d''importance (0.0 à 1.0)';

-- 8. VÉRIFICATION FINALE
-- ======================

-- Compter les tables créées
SELECT 'RESET COMPLET TERMINÉ!' as status,
       COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('jarvys_memory', 'orchestrator_logs', 'logs');

-- Vérifier les données d'initialisation
SELECT 'Données d''initialisation:' as check_type,
       (SELECT COUNT(*) FROM public.jarvys_memory) as jarvys_memory_count,
       (SELECT COUNT(*) FROM public.orchestrator_logs) as orchestrator_logs_count,
       (SELECT COUNT(*) FROM public.logs) as logs_count;

-- Afficher la structure des colonnes pour vérification
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('jarvys_memory', 'orchestrator_logs', 'logs')
ORDER BY table_name, ordinal_position;
