-- 🔧 SCRIPT SQL MINIMAL POUR GROK ORCHESTRATOR
-- ==============================================
-- Version améliorée avec schéma unifié pour JARVYS

-- Créer les tables seulement si elles n'existent pas avec schéma unifié
CREATE TABLE IF NOT EXISTS public.jarvys_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    agent_source VARCHAR(50) NOT NULL DEFAULT 'JARVYS_DEV',
    memory_type VARCHAR(50) NOT NULL DEFAULT 'experience',
    user_context VARCHAR(100) NOT NULL DEFAULT 'orchestrator',
    importance_score FLOAT NOT NULL DEFAULT 0.5 CHECK (importance_score >= 0 AND importance_score <= 1),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Colonnes de compatibilité pour ancien schéma
    session_id TEXT,
    embedding VECTOR(1536),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.orchestrator_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    agent_type VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    task TEXT,
    repo VARCHAR(50),
    status VARCHAR(50) DEFAULT 'completed',
    metadata JSONB DEFAULT '{}',
    error_details TEXT,
    success BOOLEAN DEFAULT true,
    -- Colonnes de compatibilité pour ancien schéma
    cycle_number INTEGER,
    step_name TEXT,
    content TEXT
);

CREATE TABLE IF NOT EXISTS public.logs (
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
    metadata JSONB DEFAULT '{}',
    -- Colonnes de compatibilité pour ancien schéma
    level TEXT,
    message TEXT
);

-- Index essentiels optimisés
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_memory_type ON public.jarvys_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_created_at ON public.jarvys_memory(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_session_id ON public.jarvys_memory(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_timestamp ON public.orchestrator_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_cycle ON public.orchestrator_logs(cycle_number) WHERE cycle_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON public.logs(timestamp DESC);

-- Enable RLS (Row Level Security)
ALTER TABLE public.jarvys_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orchestrator_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.logs ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust as needed)
CREATE POLICY "Allow all operations on jarvys_memory" ON public.jarvys_memory FOR ALL USING (true);
CREATE POLICY "Allow all operations on orchestrator_logs" ON public.orchestrator_logs FOR ALL USING (true);
CREATE POLICY "Allow all operations on logs" ON public.logs FOR ALL USING (true);

-- Permissions essentielles
GRANT ALL ON public.jarvys_memory TO service_role;
GRANT ALL ON public.orchestrator_logs TO service_role;
GRANT ALL ON public.logs TO service_role;

-- Test d'insertion pour vérifier
INSERT INTO public.jarvys_memory (
    content, 
    agent_source, 
    memory_type, 
    user_context, 
    importance_score, 
    tags, 
    metadata
) VALUES (
    'Test d''initialisation grok_orchestrator unifié',
    'JARVYS_DEV',
    'system_test',
    'orchestrator_initialization',
    1.0,
    ARRAY['test', 'grok', 'orchestrator', 'unified'],
    '{"test_date": "2025-07-17", "status": "operational", "schema": "unified"}'::jsonb
) ON CONFLICT DO NOTHING;

-- Vérification
SELECT 'Tables créées avec succès avec schéma unifié!' as status,
       COUNT(*) as tables_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('jarvys_memory', 'orchestrator_logs', 'logs');
