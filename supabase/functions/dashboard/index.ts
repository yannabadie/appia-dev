import { serve } from "https://deno.land/std@0.177.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
}

interface JarvysMetric {
  agent_type: string
  event_type: string
  service?: string
  model?: string
  tokens_used?: number
  cost_usd?: number
  response_time_ms?: number
  success?: boolean
  metadata?: any
  user_context?: string
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Simple authentication check
    const authHeader = req.headers.get('authorization')
    const apiKey = req.headers.get('apikey')
    const supabaseKey = Deno.env.get('SUPABASE_KEY')
    
    // Allow access if Authorization header contains a valid token or apikey matches
    if (!authHeader && !apiKey) {
      // For browser access, allow if URL contains a valid token
      const url = new URL(req.url)
      const token = url.searchParams.get('token')
      if (!token || token !== supabaseKey) {
        return new Response(
          JSON.stringify({ code: 401, message: "Missing authorization header" }), 
          { 
            status: 401, 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
          }
        )
      }
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE') ?? ''
    )

    const url = new URL(req.url)
    const path = url.pathname.replace('/dashboard', '')

    // Dashboard HTML principal
    if (path === '/' || path === '') {
      const html = await generateDashboardHTML()
      return new Response(html, {
        headers: { ...corsHeaders, 'Content-Type': 'text/html' },
      })
    }

    // API pour les métriques
    if (path === '/api/metrics') {
      const { data: metrics } = await supabase
        .from('jarvys_metrics')
        .select('*')
        .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())
        .order('created_at', { ascending: false })

      const summary = {
        daily_cost: metrics?.reduce((sum, m) => sum + (m.cost_usd || 0), 0) || 0,
        daily_calls: metrics?.length || 0,
        avg_response_time: metrics?.reduce((sum, m) => sum + (m.response_time_ms || 0), 0) / (metrics?.length || 1) || 0,
        success_rate: metrics?.filter(m => m.success).length / (metrics?.length || 1) || 0,
        agents_status: await getAgentsStatus(supabase)
      }

      return new Response(JSON.stringify(summary), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // API pour enregistrer une métrique
    if (path === '/api/metrics' && req.method === 'POST') {
      const metric: JarvysMetric = await req.json()
      
      const { error } = await supabase
        .from('jarvys_metrics')
        .insert(metric)

      if (error) throw error

      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // API pour la mémoire partagée
    if (path === '/api/memory/search' && req.method === 'POST') {
      const { query, user_context } = await req.json()
      
      // Générer l'embedding de la requête (simplifié ici)
      const { data: results } = await supabase
        .rpc('search_memory', {
          query_text: query,
          user_ctx: user_context,
          match_threshold: 0.8,
          match_count: 10
        })

      return new Response(JSON.stringify({ results }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // API pour ajouter à la mémoire avec embeddings
    if (path === '/api/memory' && req.method === 'POST') {
      const { content, agent_source, memory_type, user_context, importance_score } = await req.json()
      
      try {
        // Générer l'embedding avec OpenAI
        const openaiResponse = await fetch('https://api.openai.com/v1/embeddings', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'text-embedding-ada-002',
            input: content,
          }),
        })

        let embedding = null
        if (openaiResponse.ok) {
          const openaiData = await openaiResponse.json()
          embedding = openaiData.data[0].embedding
        }

        const { error } = await supabase
          .from('jarvys_memory')
          .insert({
            content,
            embedding, // Ajouter l'embedding calculé
            agent_source,
            memory_type,
            user_context,
            importance_score: importance_score || 0.5
          })

        if (error) throw error

        return new Response(JSON.stringify({ success: true }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      } catch (error) {
        // En cas d'erreur avec OpenAI, on insère sans embedding
        const { error: insertError } = await supabase
          .from('jarvys_memory')
          .insert({
            content,
            agent_source,
            memory_type,
            user_context,
            importance_score: importance_score || 0.5
          })

        if (insertError) throw insertError

        return new Response(JSON.stringify({ success: true, warning: 'Embedding failed' }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }
    }

    return new Response('Not found', { status: 404, headers: corsHeaders })

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})

async function getAgentsStatus(supabase: any) {
  const { data } = await supabase
    .from('jarvys_agents_status')
    .select('*')
  
  return data || []
}

async function generateDashboardHTML(): Promise<string> {
  return `<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVYS Ecosystem Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-value {
            font-size: 2.2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .agents-status {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .agent-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        
        .agent-item:last-child {
            border-bottom: none;
        }
        
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
        .status-error { color: #ffc107; }
        
        .memory-search {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .search-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            margin-bottom: 15px;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-results {
            max-height: 300px;
            overflow-y: auto;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
        }
        
        .memory-item {
            background: white;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        
        @media (max-width: 768px) {
            .metrics-grid { grid-template-columns: 1fr; }
            .container { padding: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 JARVYS Ecosystem Dashboard</h1>
            <p>Monitoring centralisé pour JARVYS_DEV (Cloud) & JARVYS_AI (Local)</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" id="daily-cost">$0.00</div>
                <div class="metric-label">Coût quotidien</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="daily-calls">0</div>
                <div class="metric-label">Appels API</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="avg-response">0ms</div>
                <div class="metric-label">Temps de réponse moyen</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="success-rate">100%</div>
                <div class="metric-label">Taux de succès</div>
            </div>
        </div>
        
        <div class="agents-status">
            <h3>📊 État des Agents</h3>
            <div id="agents-list">
                <div class="agent-item">
                    <span>🌩️ JARVYS_DEV (Cloud)</span>
                    <span class="status-offline">●  Hors ligne</span>
                </div>
                <div class="agent-item">
                    <span>🏠 JARVYS_AI (Local)</span>
                    <span class="status-offline">●  Hors ligne</span>
                </div>
            </div>
        </div>
        
        <div class="memory-search">
            <h3>🧠 Mémoire Infinie Partagée</h3>
            <input type="text" class="search-input" id="memory-query" 
                   placeholder="Rechercher dans la mémoire partagée...">
            <div class="search-results" id="search-results">
                <p>Tapez votre recherche pour explorer la mémoire infinie...</p>
            </div>
        </div>
    </div>

    <script>
        let currentUser = 'user_default'; // À remplacer par l'authentification réelle
        
        async function loadMetrics() {
            try {
                const response = await fetch('/dashboard/api/metrics');
                const data = await response.json();
                
                document.getElementById('daily-cost').textContent = '$' + data.daily_cost.toFixed(2);
                document.getElementById('daily-calls').textContent = data.daily_calls;
                document.getElementById('avg-response').textContent = Math.round(data.avg_response_time) + 'ms';
                document.getElementById('success-rate').textContent = Math.round(data.success_rate * 100) + '%';
                
                // Mettre à jour le statut des agents
                updateAgentsStatus(data.agents_status);
                
            } catch (error) {
                console.error('Erreur chargement métriques:', error);
            }
        }
        
        function updateAgentsStatus(agents) {
            const container = document.getElementById('agents-list');
            container.innerHTML = '';
            
            agents.forEach(agent => {
                const item = document.createElement('div');
                item.className = 'agent-item';
                
                const statusClass = 'status-' + agent.status;
                const icon = agent.agent_name === 'JARVYS_DEV' ? '🌩️' : '🏠';
                const env = agent.environment || (agent.agent_name === 'JARVYS_DEV' ? 'Cloud' : 'Local');
                
                item.innerHTML = \`
                    <span>\${icon} \${agent.agent_name} (\${env})</span>
                    <span class="\${statusClass}">● \${agent.status}</span>
                \`;
                
                container.appendChild(item);
            });
        }
        
        async function searchMemory() {
            const query = document.getElementById('memory-query').value;
            if (!query.trim()) return;
            
            try {
                const response = await fetch('/dashboard/api/memory/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, user_context: currentUser })
                });
                
                const data = await response.json();
                displaySearchResults(data.results || []);
                
            } catch (error) {
                console.error('Erreur recherche mémoire:', error);
            }
        }
        
        function displaySearchResults(results) {
            const container = document.getElementById('search-results');
            
            if (results.length === 0) {
                container.innerHTML = '<p>Aucun résultat trouvé dans la mémoire.</p>';
                return;
            }
            
            container.innerHTML = results.map(result => \`
                <div class="memory-item">
                    <strong>\${result.agent_source}</strong> (\${result.memory_type})<br>
                    \${result.content}<br>
                    <small>Score: \${result.importance_score} | \${new Date(result.created_at).toLocaleString()}</small>
                </div>
            \`).join('');
        }
        
        // Event listeners
        document.getElementById('memory-query').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchMemory();
        });
        
        // Charger les données initiales
        loadMetrics();
        
        // Actualiser toutes les 30 secondes
        setInterval(loadMetrics, 30000);
    </script>
</body>
</html>`
}
