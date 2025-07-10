create table if not exists public.jarvys_metrics (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default now(),
  agent_type text not null, -- 'JARVYS_DEV' ou 'JARVYS_AI'
  event_type text not null, -- 'api_call', 'task_completion', 'memory_operation', etc.
  service text, -- 'openai', 'github', 'gemini', etc.
  model text,
  tokens_used integer default 0,
  cost_usd decimal(10,4) default 0.0,
  response_time_ms integer default 0,
  success boolean default true,
  metadata jsonb default '{}',
  user_context text -- contexte utilisateur pour mémoire personnalisée
);

-- Index pour les requêtes fréquentes
create index if not exists idx_jarvys_metrics_agent_type on public.jarvys_metrics(agent_type);
create index if not exists idx_jarvys_metrics_created_at on public.jarvys_metrics(created_at);
create index if not exists idx_jarvys_metrics_event_type on public.jarvys_metrics(event_type);

-- Table pour la mémoire partagée infinie
create table if not exists public.jarvys_memory (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now(),
  agent_source text not null, -- 'JARVYS_DEV' ou 'JARVYS_AI'
  memory_type text not null, -- 'conversation', 'preference', 'knowledge', 'experience'
  content text not null,
  embedding vector(1536), -- OpenAI embeddings
  importance_score decimal(3,2) default 0.5, -- 0.0 à 1.0
  user_context text not null, -- identifiant utilisateur
  tags text[] default '{}',
  metadata jsonb default '{}'
);

-- Index pour la recherche vectorielle
create index if not exists idx_jarvys_memory_embedding on public.jarvys_memory 
using ivfflat (embedding vector_cosine_ops) with (lists = 100);

create index if not exists idx_jarvys_memory_user_context on public.jarvys_memory(user_context);
create index if not exists idx_jarvys_memory_importance on public.jarvys_memory(importance_score desc);

-- Table pour l'état des agents
create table if not exists public.jarvys_agents_status (
  agent_name text primary key,
  last_heartbeat timestamp with time zone default now(),
  status text not null default 'offline', -- 'online', 'offline', 'error', 'maintenance'
  current_task text,
  environment text, -- 'cloud', 'local', 'hybrid'
  version text,
  metadata jsonb default '{}'
);

-- Fonction pour mettre à jour le heartbeat
create or replace function update_agent_heartbeat(agent_name text, new_status text default 'online')
returns void as $$
begin
  insert into public.jarvys_agents_status (agent_name, status, last_heartbeat)
  values (agent_name, new_status, now())
  on conflict (agent_name) 
  do update set 
    last_heartbeat = now(),
    status = new_status;
end;
$$ language plpgsql security definer;

-- RLS (Row Level Security) pour la sécurité
alter table public.jarvys_metrics enable row level security;
alter table public.jarvys_memory enable row level security;
alter table public.jarvys_agents_status enable row level security;

-- Politiques RLS (permettre lecture/écriture pour les agents authentifiés)
create policy "Agents can manage their own metrics" on public.jarvys_metrics
  for all using (true); -- Simplifié pour l'instant, à sécuriser selon vos besoins

create policy "Agents can manage shared memory" on public.jarvys_memory
  for all using (true);

create policy "Public read access to agent status" on public.jarvys_agents_status
  for select using (true);

create policy "Agents can update their status" on public.jarvys_agents_status
  for all using (true);
