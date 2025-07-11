-- JARVYS Database Schema
-- Tables for JARVYS AI Agent System

-- Enable necessary extensions
create extension if not exists vector;
create extension if not exists uuid-ossp;

-- JARVYS Metrics Table
create table if not exists jarvys_metrics (
  id uuid default uuid_generate_v4() primary key,
  timestamp timestamp with time zone default now(),
  metric_type text not null,
  metric_value jsonb not null,
  agent_id text,
  session_id text,
  created_at timestamp with time zone default now()
);

-- JARVYS Memory Table (for embeddings and long-term memory)
create table if not exists jarvys_memory (
  id uuid default uuid_generate_v4() primary key,
  content text not null,
  embedding vector(1536),
  metadata jsonb default '{}',
  agent_id text,
  memory_type text default 'general',
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- JARVYS Agents Status Table
create table if not exists jarvys_agents_status (
  id uuid default uuid_generate_v4() primary key,
  agent_id text not null unique,
  status text not null default 'idle',
  current_task jsonb,
  last_activity timestamp with time zone default now(),
  performance_metrics jsonb default '{}',
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- JARVYS Tasks Table
create table if not exists jarvys_tasks (
  id uuid default uuid_generate_v4() primary key,
  task_id text not null unique,
  title text not null,
  description text,
  status text default 'pending',
  priority integer default 5,
  assigned_agent text,
  task_data jsonb default '{}',
  result jsonb,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now(),
  completed_at timestamp with time zone
);

-- JARVYS Chat History Table
create table if not exists jarvys_chat_history (
  id uuid default uuid_generate_v4() primary key,
  session_id text not null,
  message_id text not null,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  metadata jsonb default '{}',
  timestamp timestamp with time zone default now()
);

-- Create indexes for better performance
create index if not exists idx_jarvys_metrics_timestamp on jarvys_metrics(timestamp desc);
create index if not exists idx_jarvys_metrics_agent on jarvys_metrics(agent_id);
create index if not exists idx_jarvys_memory_agent on jarvys_memory(agent_id);
create index if not exists idx_jarvys_memory_type on jarvys_memory(memory_type);
create index if not exists idx_jarvys_agents_status_agent on jarvys_agents_status(agent_id);
create index if not exists idx_jarvys_tasks_status on jarvys_tasks(status);
create index if not exists idx_jarvys_tasks_agent on jarvys_tasks(assigned_agent);
create index if not exists idx_jarvys_chat_session on jarvys_chat_history(session_id);

-- Enable RLS (Row Level Security)
alter table jarvys_metrics enable row level security;
alter table jarvys_memory enable row level security;
alter table jarvys_agents_status enable row level security;
alter table jarvys_tasks enable row level security;
alter table jarvys_chat_history enable row level security;

-- Create policies for public access (adjust as needed for production)
create policy "Enable read access for all users" on jarvys_metrics for select using (true);
create policy "Enable insert access for all users" on jarvys_metrics for insert with check (true);
create policy "Enable update access for all users" on jarvys_metrics for update using (true);

create policy "Enable read access for all users" on jarvys_memory for select using (true);
create policy "Enable insert access for all users" on jarvys_memory for insert with check (true);
create policy "Enable update access for all users" on jarvys_memory for update using (true);

create policy "Enable read access for all users" on jarvys_agents_status for select using (true);
create policy "Enable insert access for all users" on jarvys_agents_status for insert with check (true);
create policy "Enable update access for all users" on jarvys_agents_status for update using (true);

create policy "Enable read access for all users" on jarvys_tasks for select using (true);
create policy "Enable insert access for all users" on jarvys_tasks for insert with check (true);
create policy "Enable update access for all users" on jarvys_tasks for update using (true);

create policy "Enable read access for all users" on jarvys_chat_history for select using (true);
create policy "Enable insert access for all users" on jarvys_chat_history for insert with check (true);
create policy "Enable update access for all users" on jarvys_chat_history for update using (true);

-- Functions for JARVYS operations

-- Function to upsert agent status
create or replace function upsert_agent_status(
  p_agent_id text,
  p_status text,
  p_current_task jsonb default null,
  p_performance_metrics jsonb default null
)
returns uuid as $$
declare
  result_id uuid;
begin
  insert into jarvys_agents_status (agent_id, status, current_task, performance_metrics, last_activity)
  values (p_agent_id, p_status, p_current_task, p_performance_metrics, now())
  on conflict (agent_id) 
  do update set 
    status = excluded.status,
    current_task = coalesce(excluded.current_task, jarvys_agents_status.current_task),
    performance_metrics = coalesce(excluded.performance_metrics, jarvys_agents_status.performance_metrics),
    last_activity = now(),
    updated_at = now()
  returning id into result_id;
  
  return result_id;
end;
$$ language plpgsql;

-- Function to get dashboard data
create or replace function get_dashboard_data()
returns jsonb as $$
declare
  result jsonb;
begin
  select jsonb_build_object(
    'agents', (
      select jsonb_agg(
        jsonb_build_object(
          'id', agent_id,
          'status', status,
          'current_task', current_task,
          'last_activity', last_activity,
          'performance_metrics', performance_metrics
        )
      )
      from jarvys_agents_status
      where last_activity > now() - interval '24 hours'
    ),
    'recent_metrics', (
      select jsonb_agg(
        jsonb_build_object(
          'timestamp', timestamp,
          'type', metric_type,
          'value', metric_value,
          'agent_id', agent_id
        )
      )
      from jarvys_metrics
      where timestamp > now() - interval '1 hour'
      order by timestamp desc
      limit 100
    ),
    'task_stats', (
      select jsonb_build_object(
        'total', count(*),
        'pending', count(*) filter (where status = 'pending'),
        'running', count(*) filter (where status = 'running'),
        'completed', count(*) filter (where status = 'completed'),
        'failed', count(*) filter (where status = 'failed')
      )
      from jarvys_tasks
      where created_at > now() - interval '24 hours'
    )
  ) into result;
  
  return result;
end;
$$ language plpgsql;

-- Grant necessary permissions
grant usage on schema public to anon, authenticated;
grant all on all tables in schema public to anon, authenticated;
grant all on all sequences in schema public to anon, authenticated;
grant execute on all functions in schema public to anon, authenticated;
