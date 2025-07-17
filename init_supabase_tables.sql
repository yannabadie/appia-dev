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

-- 3. Table pour les métriques JARVYS
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

-- 4. Table pour le contrôle d'urgence orchestrateur
CREATE TABLE IF NOT EXISTS public.orchestrator_control (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    type VARCHAR(50) NOT NULL, -- EMERGENCY_STOP, EMERGENCY_RESUME, etc.
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source VARCHAR(50) NOT NULL,
    message TEXT,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}'
);

-- 5. Table pour les suggestions d'orchestrateur
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

-- 6. Table pour les validations de tâches
CREATE TABLE IF NOT EXISTS public.task_validations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL,
    action VARCHAR(20) NOT NULL, -- approve, reject, defer
    priority INTEGER DEFAULT 3,
    comment TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validator VARCHAR(50) NOT NULL
);

-- 7. Table pour les priorités de tâches
CREATE TABLE IF NOT EXISTS public.task_priorities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL UNIQUE,
    priority INTEGER NOT NULL CHECK (priority >= 1 AND priority <= 5),
    notes TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Table pour le chat orchestrateur ↔ dashboard
CREATE TABLE IF NOT EXISTS public.orchestrator_chat (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    message TEXT NOT NULL,
    sender VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    type VARCHAR(50) DEFAULT 'user_to_orchestrator',
    status VARCHAR(20) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}'
);

-- 9. Table générique pour logs (compatibilité ancienne)
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

-- Index pour le contrôle d'urgence
CREATE INDEX IF NOT EXISTS idx_orchestrator_control_type ON public.orchestrator_control(type);
CREATE INDEX IF NOT EXISTS idx_orchestrator_control_timestamp ON public.orchestrator_control(timestamp DESC);

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

CREATE TRIGGER update_orchestrator_suggestions_updated_at 
    BEFORE UPDATE ON public.orchestrator_suggestions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_task_priorities_updated_at 
    BEFORE UPDATE ON public.task_priorities 
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
    '{"version": "1.0", "setup_date": "2025-07-16"}'::jsonb
) ON CONFLICT DO NOTHING;

-- Insérer un log d'initialisation
INSERT INTO public.orchestrator_logs (agent_type, action, task, status, metadata)
VALUES (
    'JARVYS_DEV',
    'database_init',
    'Création des tables Supabase pour écosystème JARVYS',
    'completed',
    '{"tables_created": 9, "indexes_created": 8, "triggers_created": 3}'::jsonb
) ON CONFLICT DO NOTHING;

-- 📊 POLITIQUE RLS (Row Level Security) - Optionnel
-- ================================================
-- Décommentez si vous voulez activer la sécurité au niveau des lignes

-- ALTER TABLE public.jarvys_memory ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.orchestrator_logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.jarvys_metrics ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Allow JARVYS access" ON public.jarvys_memory
--     FOR ALL USING (auth.role() = 'service_role' OR user_context = auth.jwt()->>'user_context');

COMMENT ON TABLE public.jarvys_memory IS 'Mémoire infinie partagée entre JARVYS_DEV et JARVYS_AI';
COMMENT ON TABLE public.orchestrator_logs IS 'Logs détaillés de l''orchestrateur autonome';
COMMENT ON TABLE public.jarvys_metrics IS 'Métriques de performance et monitoring JARVYS';
COMMENT ON TABLE public.orchestrator_control IS 'Signaux de contrôle d''urgence pour l''orchestrateur';

-- ✅ VÉRIFICATION
SELECT 'Base de données JARVYS initialisée avec succès!' as status,
       COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%jarvys%' OR table_name LIKE '%orchestrator%' OR table_name = 'logs';
