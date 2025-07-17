-- 🗄️ JARVYS Memory Database Schema
-- ================================
-- 
-- Script SQL pour initialiser les tables Supabase nécessaires 
-- à l'écosystème JARVYS (mémoire infinie + orchestrateur)
--
-- À exécuter dans l'éditeur SQL de Supabase Dashboard

-- 1. Table principale pour la mémoire infinie JARVYS
CREATE TABLE IF NOT EXISTS public.jarvys_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    agent_source VARCHAR(50) NOT NULL DEFAULT 'JARVYS_DEV',
    memory_type VARCHAR(50) NOT NULL DEFAULT 'experience',
    user_context VARCHAR(100) NOT NULL DEFAULT 'default',
    importance_score FLOAT NOT NULL DEFAULT 0.5 CHECK (importance_score >= 0 AND importance_score <= 1),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536), -- Pour les embeddings OpenAI text-embedding-3-small
    similarity FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Table pour les logs d'orchestrateur
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

-- 3. Table générique pour logs (compatibilité ancienne)
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

-- 4. Table pour les métriques JARVYS
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

-- 🔒 SÉCURITÉ ET OPTIMISATIONS
-- =============================

-- Index pour performance des recherches de mémoire
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_user_context ON public.jarvys_memory(user_context);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_agent_source ON public.jarvys_memory(agent_source);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_memory_type ON public.jarvys_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_importance ON public.jarvys_memory(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_created_at ON public.jarvys_memory(created_at DESC);

-- Index pour les logs d'orchestrateur
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_timestamp ON public.orchestrator_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_agent_type ON public.orchestrator_logs(agent_type);

-- Index pour les métriques
CREATE INDEX IF NOT EXISTS idx_jarvys_metrics_timestamp ON public.jarvys_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_jarvys_metrics_agent_type ON public.jarvys_metrics(agent_type);

-- Index pour logs génériques
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON public.logs(timestamp DESC);

-- 🔄 TRIGGERS pour mise à jour automatique
-- =====================================

-- Trigger pour updated_at sur jarvys_memory
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_jarvys_memory_updated_at 
    BEFORE UPDATE ON public.jarvys_memory 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 🧹 DONNÉES DE TEST ET INITIALISATION
-- ===================================

-- Insérer un exemple de mémoire pour tester
INSERT INTO public.jarvys_memory (content, agent_source, memory_type, user_context, importance_score, tags, metadata)
VALUES (
    'Initialisation du système JARVYS - Base de données créée avec succès',
    'JARVYS_DEV',
    'system',
    'initialization',
    1.0,
    ARRAY['system', 'initialization', 'database'],
    '{"version": "1.0", "setup_date": "2025-07-17"}'::jsonb
) ON CONFLICT DO NOTHING;

-- Insérer un log d'initialisation
INSERT INTO public.orchestrator_logs (agent_type, action, task, status, metadata)
VALUES (
    'JARVYS_DEV',
    'database_init',
    'Création des tables Supabase pour écosystème JARVYS',
    'completed',
    '{"tables_created": 4, "indexes_created": 6, "triggers_created": 1}'::jsonb
) ON CONFLICT DO NOTHING;

-- Grant permissions to service role
GRANT ALL ON public.jarvys_memory TO service_role;
GRANT ALL ON public.orchestrator_logs TO service_role;
GRANT ALL ON public.logs TO service_role;
GRANT ALL ON public.jarvys_metrics TO service_role;

COMMENT ON TABLE public.jarvys_memory IS 'Mémoire infinie partagée entre JARVYS_DEV et JARVYS_AI';
COMMENT ON TABLE public.orchestrator_logs IS 'Logs détaillés de l''orchestrateur autonome';
COMMENT ON TABLE public.jarvys_metrics IS 'Métriques de performance et monitoring JARVYS';
COMMENT ON TABLE public.logs IS 'Logs génériques pour compatibilité';

-- ✅ VÉRIFICATION
SELECT 'Base de données JARVYS initialisée avec succès!' as status,
       COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND (table_name LIKE '%jarvys%' OR table_name LIKE '%orchestrator%' OR table_name = 'logs');
