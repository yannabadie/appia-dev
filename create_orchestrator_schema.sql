-- JARVYS Orchestrator - Schéma Supabase Complet
-- Création des tables nécessaires pour la mémoire infinie

-- ==============================================
-- Table 1: jarvys_memory (Mémoire principale)
-- ==============================================
CREATE TABLE IF NOT EXISTS public.jarvys_memory (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    importance_score REAL DEFAULT 0.5,
    tags TEXT[] DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_session_id ON public.jarvys_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_type ON public.jarvys_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_timestamp ON public.jarvys_memory(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_importance ON public.jarvys_memory(importance_score DESC);

-- ==============================================
-- Table 2: orchestrator_logs (Logs des cycles)
-- ==============================================
CREATE TABLE IF NOT EXISTS public.orchestrator_logs (
    id BIGSERIAL PRIMARY KEY,
    cycle_number INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL,
    content TEXT DEFAULT '',
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_cycle ON public.orchestrator_logs(cycle_number);
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_status ON public.orchestrator_logs(status);
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_created_at ON public.orchestrator_logs(created_at DESC);

-- ==============================================
-- Table 3: code_validations (Validations Claude)
-- ==============================================
CREATE TABLE IF NOT EXISTS public.code_validations (
    id BIGSERIAL PRIMARY KEY,
    task_description TEXT NOT NULL,
    code_snippet TEXT NOT NULL,
    validation_result JSONB NOT NULL,
    claude_model TEXT NOT NULL,
    is_valid BOOLEAN NOT NULL,
    confidence REAL DEFAULT 0.0,
    severity_score INTEGER DEFAULT 5,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_code_validations_is_valid ON public.code_validations(is_valid);
CREATE INDEX IF NOT EXISTS idx_code_validations_confidence ON public.code_validations(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_code_validations_timestamp ON public.code_validations(timestamp DESC);

-- ==============================================
-- RLS Policies (Row Level Security)
-- ==============================================

-- Enable RLS
ALTER TABLE public.jarvys_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orchestrator_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.code_validations ENABLE ROW LEVEL SECURITY;

-- Policies pour jarvys_memory
CREATE POLICY "Enable read access for all users" ON public.jarvys_memory
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON public.jarvys_memory
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON public.jarvys_memory
    FOR UPDATE USING (true);

-- Policies pour orchestrator_logs
CREATE POLICY "Enable read access for all users" ON public.orchestrator_logs
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON public.orchestrator_logs
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON public.orchestrator_logs
    FOR UPDATE USING (true);

-- Policies pour code_validations
CREATE POLICY "Enable read access for all users" ON public.code_validations
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON public.code_validations
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON public.code_validations
    FOR UPDATE USING (true);

-- ==============================================
-- Fonctions utilitaires
-- ==============================================

-- Fonction pour nettoyer les anciennes entrées
CREATE OR REPLACE FUNCTION clean_old_memories(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.jarvys_memory 
    WHERE created_at < NOW() - INTERVAL '%s days' 
    AND importance_score < 0.3;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir les stats de mémoire
CREATE OR REPLACE FUNCTION get_memory_stats()
RETURNS TABLE(
    total_memories BIGINT,
    recent_memories BIGINT,
    avg_importance REAL,
    top_memory_types TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_memories,
        COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as recent_memories,
        AVG(importance_score) as avg_importance,
        ARRAY_AGG(DISTINCT memory_type ORDER BY COUNT(*) DESC LIMIT 5) as top_memory_types
    FROM public.jarvys_memory;
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- Commentaires et Documentation
-- ==============================================

COMMENT ON TABLE public.jarvys_memory IS 'Stockage de la mémoire infinie de l''orchestrateur JARVYS';
COMMENT ON TABLE public.orchestrator_logs IS 'Logs des cycles d''exécution de l''orchestrateur';
COMMENT ON TABLE public.code_validations IS 'Résultats des validations de code par Claude 4';

COMMENT ON COLUMN public.jarvys_memory.session_id IS 'Identifiant de session unique';
COMMENT ON COLUMN public.jarvys_memory.memory_type IS 'Type de mémoire (code_generation, validation, etc.)';
COMMENT ON COLUMN public.jarvys_memory.importance_score IS 'Score d''importance de 0.0 à 1.0';
COMMENT ON COLUMN public.jarvys_memory.tags IS 'Tags pour catégoriser les mémoires';

-- ==============================================
-- Vérification finale
-- ==============================================

-- Vérifier que toutes les tables existent
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jarvys_memory') THEN
        RAISE NOTICE 'Table jarvys_memory créée avec succès';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orchestrator_logs') THEN
        RAISE NOTICE 'Table orchestrator_logs créée avec succès';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'code_validations') THEN
        RAISE NOTICE 'Table code_validations créée avec succès';
    END IF;
END $$;
