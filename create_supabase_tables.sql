-- create_supabase_tables.sql
-- Tables nécessaires pour Claude 4 Opus Agent

-- 1. Table des logs de l'agent
CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    agent TEXT NOT NULL,
    activity TEXT NOT NULL,
    status TEXT,
    costs DECIMAL(10, 4) DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    error_message TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Table des corrections en attente
CREATE TABLE IF NOT EXISTS pending_fixes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    repo TEXT NOT NULL,
    branch_name TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    issue_description TEXT,
    file_path TEXT,
    pr_created BOOLEAN DEFAULT FALSE,
    pr_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Table des suggestions d'amélioration
CREATE TABLE IF NOT EXISTS improvement_suggestions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    suggestions TEXT,
    agent TEXT,
    implemented BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Table logs (mentionnée dans votre config)
CREATE TABLE IF NOT EXISTS logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    status TEXT,
    error TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent ON agent_logs(agent);
CREATE INDEX IF NOT EXISTS idx_agent_logs_costs ON agent_logs(costs);
CREATE INDEX IF NOT EXISTS idx_pending_fixes_repo ON pending_fixes(repo);
CREATE INDEX IF NOT EXISTS idx_pending_fixes_pr_created ON pending_fixes(pr_created);

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger pour pending_fixes
DROP TRIGGER IF EXISTS update_pending_fixes_updated_at ON pending_fixes;
CREATE TRIGGER update_pending_fixes_updated_at 
    BEFORE UPDATE ON pending_fixes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Vue pour le monitoring des coûts quotidiens
CREATE OR REPLACE VIEW daily_costs AS
SELECT 
    DATE(timestamp) as date,
    agent,
    COUNT(*) as total_runs,
    SUM(costs) as total_costs,
    AVG(costs) as avg_cost_per_run,
    SUM(tasks_completed) as total_tasks
FROM agent_logs
GROUP BY DATE(timestamp), agent
ORDER BY date DESC;

-- Vue pour les erreurs récentes
CREATE OR REPLACE VIEW recent_errors AS
SELECT 
    timestamp,
    agent,
    activity,
    error_message,
    details
FROM agent_logs
WHERE status = 'error'
    AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Permissions (si Row Level Security est activé)
ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE pending_fixes ENABLE ROW LEVEL SECURITY;
ALTER TABLE improvement_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- Politique pour permettre toutes les opérations (à ajuster selon vos besoins)
CREATE POLICY "Enable all operations" ON agent_logs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all operations" ON pending_fixes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all operations" ON improvement_suggestions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all operations" ON logs FOR ALL USING (true) WITH CHECK (true);

-- Données de test pour vérifier
INSERT INTO agent_logs (agent, activity, status, costs, tasks_completed)
VALUES ('claude_4_opus', 'test_installation', 'success', 0.0, 1);

-- Afficher un résumé
SELECT 'Tables créées avec succès!' as message;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('agent_logs', 'pending_fixes', 'improvement_suggestions', 'logs');