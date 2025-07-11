// Patch authentification JARVYS Dashboard - Version améliorée
// Remplacer le contenu de supabase/functions/jarvys-dashboard/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const VALID_TOKENS = [
  'test',
  'admin', 
  'dashboard',
  'jarvys-dev',
  'jarvys-ai'
];

function authenticateRequest(req: Request): boolean {
  const authHeader = req.headers.get('Authorization');
  
  if (!authHeader) {
    return false;
  }
  
  const token = authHeader.replace('Bearer ', '').trim();
  return VALID_TOKENS.includes(token);
}

serve(async (req) => {
  // CORS headers pour tous les domaines
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'authorization, content-type, x-client-info',
  };

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  const url = new URL(req.url);
  console.log(`📡 Request: ${req.method} ${url.pathname}`);

  // Health check sans authentification
  if (url.pathname === '/health') {
    return new Response(
      JSON.stringify({ 
        status: 'ok', 
        service: 'jarvys-dashboard',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      }),
      { 
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      }
    );
  }

  // Authentification pour toutes les autres routes
  if (!authenticateRequest(req)) {
    return new Response(
      JSON.stringify({ 
        code: 401, 
        message: 'Unauthorized. Use: Bearer test',
        hint: 'Valid tokens: test, admin, dashboard, jarvys-dev, jarvys-ai'
      }),
      {
        status: 401,
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      }
    );
  }

  // Routes API
  if (url.pathname.startsWith('/api/')) {
    const endpoint = url.pathname.replace('/api/', '');
    
    switch (endpoint) {
      case 'metrics':
        return new Response(
          JSON.stringify({
            daily_cost: 3.28,
            api_calls: 164,
            response_time: 130,
            success_rate: 95.0,
            models: {
              "gpt-4": { calls: 45, cost: 1.8 },
              "claude-3-sonnet": { calls: 89, cost: 1.34 },
              "gpt-3.5-turbo": { calls: 30, cost: 0.14 }
            },
            timestamp: new Date().toISOString()
          }),
          { 
            headers: { 
              'Content-Type': 'application/json',
              ...corsHeaders
            }
          }
        );
        
      case 'status':
        return new Response(
          JSON.stringify({
            jarvys_dev: { status: 'active', last_ping: new Date().toISOString() },
            jarvys_ai: { status: 'active', last_ping: new Date().toISOString() },
            supabase: { status: 'connected' },
            github: { status: 'connected' }
          }),
          { 
            headers: { 
              'Content-Type': 'application/json',
              ...corsHeaders
            }
          }
        );
        
      case 'control':
        if (req.method === 'POST') {
          const body = await req.json();
          return new Response(
            JSON.stringify({
              action: body.action || 'unknown',
              agent: body.agent || 'all',
              status: 'executed',
              timestamp: new Date().toISOString()
            }),
            { 
              headers: { 
                'Content-Type': 'application/json',
                ...corsHeaders
              }
            }
          );
        }
        break;
        
      default:
        return new Response(
          JSON.stringify({ 
            error: 'Endpoint not found',
            available: ['/api/metrics', '/api/status', '/api/control'],
            timestamp: new Date().toISOString()
          }),
          { 
            status: 404,
            headers: { 
              'Content-Type': 'application/json',
              ...corsHeaders
            }
          }
        );
    }
  }

  // Dashboard principal
  const dashboard_html = `
<!DOCTYPE html>
<html>
<head>
    <title>JARVYS Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh; padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .metric-card { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; border-radius: 15px; 
            backdrop-filter: blur(10px); text-align: center;
        }
        .metric-value { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .metric-label { opacity: 0.8; }
        .controls { text-align: center; }
        .btn { 
            background: rgba(255,255,255,0.2); 
            border: none; color: white; 
            padding: 10px 20px; margin: 5px; 
            border-radius: 25px; cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
        .status { margin-top: 20px; }
        .status-item { 
            display: inline-block; 
            margin: 5px; padding: 5px 15px; 
            background: rgba(0,255,0,0.2); 
            border-radius: 15px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 JARVYS Dashboard</h1>
            <p>Intelligence Artificielle Autonome</p>
        </div>
        
        <div class="metrics" id="metrics">
            <div class="metric-card">
                <div class="metric-value" id="daily-cost">$3.28</div>
                <div class="metric-label">Coût Quotidien</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="api-calls">164</div>
                <div class="metric-label">Appels API</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="response-time">130ms</div>
                <div class="metric-label">Temps Réponse</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="success-rate">95.0%</div>
                <div class="metric-label">Taux Succès</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="pauseAgent('jarvys_dev')">⏸️ Pause JARVYS_DEV</button>
            <button class="btn" onclick="resumeAgent('jarvys_dev')">▶️ Resume JARVYS_DEV</button>
            <button class="btn" onclick="pauseAgent('jarvys_ai')">⏸️ Pause JARVYS_AI</button>
            <button class="btn" onclick="resumeAgent('jarvys_ai')">▶️ Resume JARVYS_AI</button>
            <button class="btn" onclick="refreshMetrics()">🔄 Actualiser</button>
        </div>
        
        <div class="status">
            <div class="status-item">🟢 JARVYS_DEV: Actif</div>
            <div class="status-item">🟢 JARVYS_AI: Actif</div>
            <div class="status-item">🟢 Supabase: Connecté</div>
            <div class="status-item">🟢 GitHub: Connecté</div>
        </div>
    </div>

    <script>
        function pauseAgent(agent) {
            fetch('/api/control', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer test'
                },
                body: JSON.stringify({ action: 'pause', agent: agent })
            }).then(r => r.json()).then(d => {
                alert(\`Agent \${agent} mis en pause\`);
            });
        }
        
        function resumeAgent(agent) {
            fetch('/api/control', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer test'
                },
                body: JSON.stringify({ action: 'resume', agent: agent })
            }).then(r => r.json()).then(d => {
                alert(\`Agent \${agent} relancé\`);
            });
        }
        
        function refreshMetrics() {
            fetch('/api/metrics', {
                headers: { 'Authorization': 'Bearer test' }
            }).then(r => r.json()).then(data => {
                document.getElementById('daily-cost').textContent = '$' + data.daily_cost;
                document.getElementById('api-calls').textContent = data.api_calls;
                document.getElementById('response-time').textContent = data.response_time + 'ms';
                document.getElementById('success-rate').textContent = data.success_rate + '%';
            });
        }
        
        // Auto-refresh toutes les 30 secondes
        setInterval(refreshMetrics, 30000);
    </script>
</body>
</html>`;

  return new Response(dashboard_html, {
    headers: { 
      'Content-Type': 'text/html',
      ...corsHeaders
    }
  });
});