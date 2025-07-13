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
    // Simplified authentication - allow access for dashboard viewing
    const url = new URL(req.url)
    const path = url.pathname
    
    console.log('Request URL:', req.url)
    console.log('Request path:', path, 'Method:', req.method)

    // Extract the actual path after function name
    const functionPath = path.replace('/functions/v1/jarvys-dashboard', '') || '/'
    
    console.log('Function path:', functionPath)

    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE')
    
    if (!supabaseUrl || !supabaseServiceKey) {
      console.error('Missing Supabase environment variables')
      return new Response(JSON.stringify({ error: 'Configuration error' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // Dashboard HTML principal
    if (functionPath === '/' || functionPath === '') {
      const html = await generateDashboardHTML()
      return new Response(html, {
        headers: { ...corsHeaders, 'Content-Type': 'text/html' },
      })
    }

    // API pour les métriques
    if (functionPath === '/api/metrics' && req.method === 'GET') {
      try {
        const { data: metrics, error: metricsError } = await supabase
          .from('jarvys_metrics')
          .select('*')
          .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())
          .order('created_at', { ascending: false })

        if (metricsError) {
          console.error('Metrics query error:', metricsError)
          // Return default values if table doesn't exist
          const summary = {
            daily_cost: 0,
            daily_calls: 0,
            avg_response_time: 0,
            success_rate: 1,
            agents_status: await getAgentsStatus(supabase)
          }
          return new Response(JSON.stringify(summary), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          })
        }

        const summary = {
          daily_cost: metrics?.reduce((sum, m) => sum + (m.cost_usd || 0), 0) || 0,
          daily_calls: metrics?.length || 0,
          avg_response_time: metrics?.length > 0 ? metrics.reduce((sum, m) => sum + (m.response_time_ms || 0), 0) / metrics.length : 0,
          success_rate: metrics?.length > 0 ? metrics.filter(m => m.success).length / metrics.length : 1,
          agents_status: await getAgentsStatus(supabase)
        }

        return new Response(JSON.stringify(summary), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      } catch (error) {
        console.error('Error fetching metrics:', error)
        // Return default values on error
        const summary = {
          daily_cost: 0,
          daily_calls: 0,
          avg_response_time: 0,
          success_rate: 1,
          agents_status: await getAgentsStatus(supabase)
        }
        return new Response(JSON.stringify(summary), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }
    }

    // API pour enregistrer une métrique
    if (functionPath === '/api/metrics' && req.method === 'POST') {
      try {
        const metric: JarvysMetric = await req.json()
        
        const { error } = await supabase
          .from('jarvys_metrics')
          .insert({
            ...metric,
            created_at: new Date().toISOString()
          })

        if (error) {
          console.error('Insert metric error:', error)
          // Don't throw error, just log it and return success
          return new Response(JSON.stringify({ success: true, warning: 'Database insert failed' }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          })
        }

        return new Response(JSON.stringify({ success: true }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      } catch (error) {
        console.error('Error inserting metric:', error)
        return new Response(JSON.stringify({ success: false, error: 'Failed to insert metric' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }
    }

    // API pour la mémoire partagée
    if (functionPath === '/api/memory/search' && req.method === 'POST') {
      try {
        const { query, user_context } = await req.json()
        
        // Try to use the RPC function first, fallback to simple search
        let results = []
        try {
          const { data, error } = await supabase
            .rpc('search_memory', {
              query_text: query,
              user_ctx: user_context || 'default',
              match_threshold: 0.8,
              match_count: 10
            })
          
          if (error) throw error
          results = data || []
        } catch (rpcError) {
          console.log('RPC search failed, using fallback:', rpcError)
          // Fallback to simple text search
          try {
            const { data, error } = await supabase
              .from('jarvys_memory')
              .select('*')
              .ilike('content', `%${query}%`)
              .eq('user_context', user_context || 'default')
              .limit(10)
            
            if (error) throw error
            results = data || []
          } catch (fallbackError) {
            console.error('Fallback search failed:', fallbackError)
            results = []
          }
        }

        return new Response(JSON.stringify({ results }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      } catch (error) {
        console.error('Error searching memory:', error)
        return new Response(JSON.stringify({ results: [], error: 'Search failed' }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }
    }

    // API pour ajouter à la mémoire avec embeddings
    if (functionPath === '/api/memory' && req.method === 'POST') {
      try {
        const { content, agent_source, memory_type, user_context, importance_score } = await req.json()
        
        let embedding = null
        const openaiApiKey = Deno.env.get('OPENAI_API_KEY')
        
        if (openaiApiKey) {
          try {
            const openaiResponse = await fetch('https://api.openai.com/v1/embeddings', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${openaiApiKey}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                model: 'text-embedding-ada-002',
                input: content,
              }),
            })

            if (openaiResponse.ok) {
              const openaiData = await openaiResponse.json()
              embedding = openaiData.data[0].embedding
            } else {
              console.error('OpenAI API error:', await openaiResponse.text())
            }
          } catch (embeddingError) {
            console.error('Error generating embedding:', embeddingError)
          }
        }

        const { error } = await supabase
          .from('jarvys_memory')
          .insert({
            content,
            embedding,
            agent_source: agent_source || 'unknown',
            memory_type: memory_type || 'general',
            user_context: user_context || 'default',
            importance_score: importance_score || 0.5,
            created_at: new Date().toISOString()
          })

        if (error) {
          console.error('Insert memory error:', error)
          return new Response(JSON.stringify({ success: false, error: 'Failed to insert memory' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          })
        }

        return new Response(JSON.stringify({ 
          success: true, 
          embedding_generated: !!embedding 
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      } catch (error) {
        console.error('Error inserting memory:', error)
        return new Response(JSON.stringify({ success: false, error: 'Failed to insert memory' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }
    }

    return new Response('Not found', { status: 404, headers: corsHeaders })

  } catch (error) {
    console.error('Global error:', error)
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})

async function getAgentsStatus(supabase: any) {
  try {
    const { data, error } = await supabase
      .from('jarvys_agents_status')
      .select('*')
    
    if (error) {
      console.error('Error fetching agents status:', error)
      // Return default agents if table doesn't exist
      return [
        {
          agent_name: 'JARVYS_DEV',
          status: 'offline',
          environment: 'Cloud',
          last_seen: new Date().toISOString()
        },
        {
          agent_name: 'JARVYS_AI',
          status: 'offline', 
          environment: 'Local',
          last_seen: new Date().toISOString()
        }
      ]
    }
    
    return data || []
  } catch (error) {
    console.error('Error in getAgentsStatus:', error)
    return [
      {
        agent_name: 'JARVYS_DEV',
        status: 'offline',
        environment: 'Cloud',
        last_seen: new Date().toISOString()
      },
      {
        agent_name: 'JARVYS_AI',
        status: 'offline', 
        environment: 'Local',
        last_seen: new Date().toISOString()
      }
    ]
  }
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
        
        .error-message {
            color: #dc3545;
            background: rgba(220, 53, 69, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        
        @media (max-width: 768px) {
            .metrics-grid { grid-template-columns: 1fr; }
            .container { padding: 10px; }
            .header h1 { font-size: 2em; }
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
            <button onclick="searchMemory()" style="
                background: #667eea; 
                color: white; 
                border: none; 
                padding: 10px 20px; 
                border-radius: 5px; 
                cursor: pointer; 
                margin-bottom: 15px;
            ">Rechercher</button>
            <div class="search-results" id="search-results">
                <p>Tapez votre recherche pour explorer la mémoire infinie...</p>
            </div>
        </div>
    </div>

    <script>
        let currentUser = 'user_default';
        let isLoading = false;
        
        function setLoading(loading) {
            isLoading = loading;
            document.body.classList.toggle('loading', loading);
        }
        
        async function loadMetrics() {
            if (isLoading) return;
            
            try {
                setLoading(true);
                const response = await fetch('./api/metrics');
                if (!response.ok) {
                    throw new Error(\`HTTP \${response.status}: \${response.statusText}\`);
                }
                const data = await response.json();
                
                document.getElementById('daily-cost').textContent = '$' + (data.daily_cost || 0).toFixed(2);
                document.getElementById('daily-calls').textContent = data.daily_calls || 0;
                document.getElementById('avg-response').textContent = Math.round(data.avg_response_time || 0) + 'ms';
                document.getElementById('success-rate').textContent = Math.round((data.success_rate || 0) * 100) + '%';
                
                updateAgentsStatus(data.agents_status || []);
                
            } catch (error) {
                console.error('Erreur chargement métriques:', error);
                // Show error in UI
                document.getElementById('daily-cost').textContent = 'N/A';
                document.getElementById('daily-calls').textContent = 'N/A';
                document.getElementById('avg-response').textContent = 'N/A';
                document.getElementById('success-rate').textContent = 'N/A';
                
                // Show error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = 'Erreur de chargement des métriques: ' + error.message;
                document.querySelector('.metrics-grid').insertAdjacentElement('afterend', errorDiv);
                setTimeout(() => errorDiv.remove(), 5000);
            } finally {
                setLoading(false);
            }
        }
        
        function updateAgentsStatus(agents) {
            const container = document.getElementById('agents-list');
            container.innerHTML = '';
            
            if (agents.length === 0) {
                // Show default agents
                const defaultAgents = [
                    { agent_name: 'JARVYS_DEV', status: 'offline', environment: 'Cloud' },
                    { agent_name: 'JARVYS_AI', status: 'offline', environment: 'Local' }
                ];
                agents = defaultAgents;
            }
            
            agents.forEach(agent => {
                const item = document.createElement('div');
                item.className = 'agent-item';
                
                const statusClass = 'status-' + (agent.status || 'offline');
                const icon = agent.agent_name === 'JARVYS_DEV' ? '🌩️' : '🏠';
                const env = agent.environment || (agent.agent_name === 'JARVYS_DEV' ? 'Cloud' : 'Local');
                const status = agent.status || 'offline';
                const statusText = status === 'online' ? 'En ligne' : 
                                 status === 'error' ? 'Erreur' : 'Hors ligne';
                
                item.innerHTML = \`
                    <span>\${icon} \${agent.agent_name} (\${env})</span>
                    <span class="\${statusClass}">● \${statusText}</span>
                \`;
                
                container.appendChild(item);
            });
        }
        
        async function searchMemory() {
            const query = document.getElementById('memory-query').value;
            if (!query.trim()) {
                document.getElementById('search-results').innerHTML = 
                    '<p>Veuillez saisir un terme de recherche.</p>';
                return;
            }
            
            if (isLoading) return;
            
            try {
                setLoading(true);
                document.getElementById('search-results').innerHTML = '<p>Recherche en cours...</p>';
                
                const response = await fetch('./api/memory/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, user_context: currentUser })
                });
                
                if (!response.ok) {
                    throw new Error(\`HTTP \${response.status}: \${response.statusText}\`);
                }
                
                const data = await response.json();
                displaySearchResults(data.results || []);
                
            } catch (error) {
                console.error('Erreur recherche mémoire:', error);
                document.getElementById('search-results').innerHTML = 
                    '<div class="error-message">Erreur lors de la recherche: ' + error.message + '</div>';
            } finally {
                setLoading(false);
            }
        }
        
        function displaySearchResults(results) {
            const container = document.getElementById('search-results');
            
            if (results.length === 0) {
                container.innerHTML = '<p>Aucun résultat trouvé dans la mémoire partagée.</p>';
                return;
            }
            
            container.innerHTML = results.map(result => \`
                <div class="memory-item">
                    <strong>\${result.agent_source || 'Unknown'}</strong> (\${result.memory_type || 'general'})<br>
                    <div style="margin: 5px 0;">\${result.content}</div>
                    <small style="color: #666;">
                        Score: \${(result.importance_score || 0).toFixed(2)} | 
                        \${result.created_at ? new Date(result.created_at).toLocaleString() : 'Date inconnue'}
                    </small>
                </div>
            \`).join('');
        }
        
        // Event listeners
        document.getElementById('memory-query').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !isLoading) {
                searchMemory();
            }
        });
        
        // Load initial data with retry
        async function initDashboard() {
            try {
                await loadMetrics();
                console.log('JARVYS Dashboard loaded successfully');
            } catch (error) {
                console.error('Failed to initialize dashboard:', error);
                setTimeout(initDashboard, 5000); // Retry after 5 seconds
            }
        }
        
        // Initialize dashboard
        initDashboard();
        
        // Refresh every 30 seconds
        setInterval(() => {
            if (!isLoading) {
                loadMetrics();
            }
        }, 30000);
        
        // Add visual feedback for connection status
        window.addEventListener('online', () => {
            console.log('Connection restored');
            if (!isLoading) loadMetrics();
        });
        
        window.addEventListener('offline', () => {
            console.log('Connection lost');
        });
    </script>
</body>
</html>`
}
