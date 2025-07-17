-- 🔧 SCRIPT SQL MINIMAL POUR GROK ORCHESTRATOR
-- ==============================================
-- Version simplifiée sans suppression, juste création des tables nécessaires

-- Complete Supabase setup for orchestrator
-- Drop existing tables if they exist
DROP TABLE IF EXISTS jarvys_memory CASCADE;
DROP TABLE IF EXISTS orchestrator_logs CASCADE;
DROP TABLE IF EXISTS logs CASCADE;

-- Create jarvys_memory table with ALL required columns
CREATE TABLE jarvys_memory (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    memory_type TEXT NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create orchestrator_logs table with ALL required columns  
CREATE TABLE orchestrator_logs (
    id SERIAL PRIMARY KEY,
    cycle_number INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL,
    content TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create logs table with ALL required columns
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Enable RLS (Row Level Security)
ALTER TABLE jarvys_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE orchestrator_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust as needed)
CREATE POLICY "Allow all operations on jarvys_memory" ON jarvys_memory FOR ALL USING (true);
CREATE POLICY "Allow all operations on orchestrator_logs" ON orchestrator_logs FOR ALL USING (true);
CREATE POLICY "Allow all operations on logs" ON logs FOR ALL USING (true);

-- Create indexes for performance
CREATE INDEX idx_jarvys_memory_session_id ON jarvys_memory(session_id);
CREATE INDEX idx_jarvys_memory_timestamp ON jarvys_memory(timestamp);
CREATE INDEX idx_jarvys_memory_memory_type ON jarvys_memory(memory_type);
CREATE INDEX idx_orchestrator_logs_cycle ON orchestrator_logs(cycle_number);
CREATE INDEX idx_orchestrator_logs_timestamp ON orchestrator_logs(timestamp);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);

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
