-- Fonction RPC pour recherche dans la mémoire vectorielle
create or replace function search_memory(
  query_text text,
  user_ctx text,
  match_threshold float default 0.8,
  match_count int default 10
)
returns table (
  id uuid,
  content text,
  agent_source text,
  memory_type text,
  importance_score decimal,
  similarity float,
  created_at timestamptz,
  tags text[],
  metadata jsonb
)
language sql
as $$
  select
    jm.id,
    jm.content,
    jm.agent_source,
    jm.memory_type,
    jm.importance_score,
    (jm.embedding <=> query_embedding.embedding) as similarity,
    jm.created_at,
    jm.tags,
    jm.metadata
  from jarvys_memory jm
  cross join (
    select embedding::vector as embedding
    from ai_embedding('text-embedding-3-small', query_text)
  ) as query_embedding
  where jm.user_context = user_ctx
    and (jm.embedding <=> query_embedding.embedding) < (1 - match_threshold)
  order by jm.embedding <=> query_embedding.embedding
  limit match_count;
$$;

-- Fonction pour mettre à jour automatiquement updated_at
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Trigger pour updated_at sur jarvys_memory
create trigger update_jarvys_memory_updated_at
  before update on public.jarvys_memory
  for each row
  execute function update_updated_at_column();

-- Vue pour les statistiques du dashboard
create or replace view dashboard_stats as
select
  date_trunc('hour', created_at) as hour,
  agent_type,
  event_type,
  service,
  count(*) as event_count,
  sum(cost_usd) as total_cost,
  avg(response_time_ms) as avg_response_time,
  sum(case when success then 1 else 0 end)::float / count(*) as success_rate
from jarvys_metrics
where created_at >= now() - interval '24 hours'
group by hour, agent_type, event_type, service
order by hour desc;

-- Vue pour l'activité récente
create or replace view recent_activity as
select
  created_at,
  agent_type,
  event_type,
  service,
  model,
  success,
  metadata
from jarvys_metrics
where created_at >= now() - interval '6 hours'
order by created_at desc
limit 50;
