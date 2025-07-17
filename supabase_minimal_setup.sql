-- 🔧 SCRIPT SQL MINIMAL POUR GROK ORCHESTRATOR
-- ==============================================
-- Version simplifiée sans suppression, juste création des tables nécessaires

-- Créer les tables seulement si elles n'existent pas
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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    success BOOLEAN DEFAULT true
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
    metadata JSONB DEFAULT '{}'
);

-- Index essentiels
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_memory_type ON public.jarvys_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_jarvys_memory_created_at ON public.jarvys_memory(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_timestamp ON public.orchestrator_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON public.logs(timestamp DESC);

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
    'Test d''initialisation grok_orchestrator',
    'JARVYS_DEV',
    'system_test',
    'orchestrator_initialization',
    1.0,
    ARRAY['test', 'grok', 'orchestrator'],
    '{"test_date": "2025-07-17", "status": "operational"}'::jsonb
) ON CONFLICT DO NOTHING;

-- Vérification
SELECT 'Tables créées avec succès!' as status,
       COUNT(*) as tables_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('jarvys_memory', 'orchestrator_logs', 'logs');
