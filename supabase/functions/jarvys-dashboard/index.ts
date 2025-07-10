// JARVYS Dashboard Edge Function for Supabase
// Provides a cloud-hosted dashboard for the JARVYS DevOps agent

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Secret d'authentification pour les Edge Functions
const EDGE_FUNCTION_SECRET = (globalThis as any).Deno?.env?.get('SPB_EDGE_FUNCTIONS') || 'dHx8o@3?G4!QT86C';

interface JarvysMetrics {
  daily_cost_usd: number;
  daily_api_calls: number;
  total_interactions: number;
  active_models: number;
  system_uptime: number;
  memory_usage: number;
}

interface DashboardData {
  metrics: JarvysMetrics;
  status: {
    active: boolean;
    version: string;
    uptime: string;
    last_loop: string;
  };
  recent_tasks: Array<{
    id: string;
    timestamp: string;
    type: string;
    status: string;
    description: string;
  }>;
}

// Simulation des données JARVYS pour l'environnement cloud
function getMockJarvysData(): DashboardData {
  const now = new Date();
  const uptimeHours = Math.floor(Math.random() * 168) + 1;
  
  return {
    metrics: {
      daily_cost_usd: Math.round((Math.random() * 5 + 1) * 100) / 100,
      daily_api_calls: Math.floor(Math.random() * 300 + 50),
      total_interactions: Math.floor(Math.random() * 50 + 10),
      active_models: 3,
      system_uptime: uptimeHours,
      memory_usage: Math.floor(Math.random() * 200 + 300)
    },
    status: {
      active: true,
      version: "1.0.0-cloud",
      uptime: `${uptimeHours}h ${Math.floor(Math.random() * 60)}m`,
      last_loop: now.toISOString()
    },
    recent_tasks: [
      {
        id: "task_" + Math.random().toString(36).substr(2, 9),
        timestamp: new Date(now.getTime() - Math.random() * 3600000).toISOString(),
        type: "model_optimization",
        status: "completed",
        description: "Optimized Claude 4 Sonnet routing for cost efficiency"
      },
      {
        id: "task_" + Math.random().toString(36).substr(2, 9),
        timestamp: new Date(now.getTime() - Math.random() * 7200000).toISOString(),
        type: "security_scan",
        status: "completed",
        description: "Performed security audit on API endpoints"
      },
      {
        id: "task_" + Math.random().toString(36).substr(2, 9),
        timestamp: new Date(now.getTime() - Math.random() * 10800000).toISOString(),
        type: "performance_monitoring",
        status: "in_progress",
        description: "Monitoring Gemini 2.5 Pro response latency"
      }
    ]
  };
}

// Template HTML principal du dashboard
function getDashboardHTML(data: DashboardData): string {
  return `<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVYS_DEV Cloud Dashboard</title>
    <style>
        :root {
            --primary-bg: #0D1117;
            --secondary-bg: #161B22;
            --accent-bg: #21262D;
            --text-primary: #F0F6FC;
            --text-secondary: #8B949E;
            --accent-blue: #58A6FF;
            --accent-green: #3FB950;
            --accent-orange: #FF8C00;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, var(--primary-bg) 0%, #1a1f2e 100%);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }
        .header {
            background: var(--secondary-bg);
            padding: 1.5rem 2rem;
            border-bottom: 1px solid var(--accent-bg);
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .logo { display: flex; align-items: center; gap: 12px; }
        .logo h1 {
            color: var(--accent-blue);
            font-size: 1.8rem;
            font-weight: 700;
        }
        .cloud-badge {
            background: linear-gradient(135deg, var(--accent-green), #56d364);
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--accent-bg);
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 0.95rem;
            border: 1px solid var(--accent-green);
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .main-content {
            padding: 2.5rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        .metric-card {
            background: var(--secondary-bg);
            border: 1px solid var(--accent-bg);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-blue);
            box-shadow: 0 8px 25px rgba(88, 166, 255, 0.2);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--accent-blue);
            margin-bottom: 0.5rem;
        }
        .metric-label {
            color: var(--text-secondary);
            font-size: 1rem;
            margin-bottom: 0.8rem;
            font-weight: 500;
        }
        .metric-change {
            font-size: 0.85rem;
            padding: 6px 12px;
            border-radius: 15px;
            display: inline-block;
            font-weight: 600;
            background: rgba(63, 185, 80, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(63, 185, 80, 0.3);
        }
        .tasks-section {
            background: var(--secondary-bg);
            border: 1px solid var(--accent-bg);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        .section-title {
            color: var(--text-primary);
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
        }
        .task-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem;
            border: 1px solid var(--accent-bg);
            border-radius: 8px;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            background: rgba(33, 38, 45, 0.5);
        }
        .task-info { flex: 1; }
        .task-title {
            color: var(--text-primary);
            font-weight: 600;
            margin-bottom: 6px;
            font-size: 1.1rem;
        }
        .task-description {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .task-timestamp {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 6px;
        }
        .task-status {
            padding: 8px 16px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .status-completed {
            background: rgba(63, 185, 80, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(63, 185, 80, 0.3);
        }
        .status-in-progress {
            background: rgba(255, 140, 0, 0.15);
            color: var(--accent-orange);
            border: 1px solid rgba(255, 140, 0, 0.3);
        }
        .refresh-btn {
            background: linear-gradient(135deg, var(--accent-blue), #4A9EFF);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .footer {
            text-align: center;
            padding: 3rem 2rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--accent-bg);
            margin-top: 3rem;
            background: var(--secondary-bg);
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">
            <h1>🤖 JARVYS_DEV</h1>
            <span class="cloud-badge">☁️ CLOUD</span>
        </div>
        <div class="status-badge">
            <span class="status-indicator"></span>
            Agent DevOps autonome actif
        </div>
    </header>
    <main class="main-content">
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">$${data.metrics.daily_cost_usd}</div>
                <div class="metric-label">Coût quotidien (USD)</div>
                <div class="metric-change">📈 Optimisé</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data.metrics.daily_api_calls}</div>
                <div class="metric-label">Appels API aujourd'hui</div>
                <div class="metric-change">🚀 Multi-modèles</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data.metrics.total_interactions}</div>
                <div class="metric-label">Interactions totales</div>
                <div class="metric-change">🔄 Temps réel</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data.metrics.active_models}</div>
                <div class="metric-label">Modèles IA actifs</div>
                <div class="metric-change">🧠 Claude • GPT • Gemini</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data.metrics.system_uptime}h</div>
                <div class="metric-label">Uptime système</div>
                <div class="metric-change">✅ 99.9%</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${data.metrics.memory_usage}MB</div>
                <div class="metric-label">Mémoire utilisée</div>
                <div class="metric-change">💾 Edge optimisé</div>
            </div>
        </div>
        <div class="tasks-section">
            <div class="section-title">
                📋 Tâches autonomes récentes
                <button class="refresh-btn" onclick="location.reload()">🔄 Actualiser</button>
            </div>
            ${data.recent_tasks.map(task => `
                <div class="task-item">
                    <div class="task-info">
                        <div class="task-title">${task.type.replace(/_/g, ' ').toUpperCase()}</div>
                        <div class="task-description">${task.description}</div>
                        <div class="task-timestamp">🕐 ${new Date(task.timestamp).toLocaleString('fr-FR')}</div>
                    </div>
                    <div class="task-status status-${task.status.replace('_', '-')}">${task.status.replace('_', ' ')}</div>
                </div>
            `).join('')}
        </div>
    </main>
    <footer class="footer">
        <p>🚀 <strong>JARVYS_DEV Cloud Dashboard</strong> - Powered by Supabase Edge Functions</p>
        <p>Version ${data.status.version} • ${new Date(data.status.last_loop).toLocaleString('fr-FR')}</p>
    </footer>
    <script>
        setInterval(() => location.reload(), 30000);
        console.log("🤖 JARVYS_DEV Cloud Dashboard - Edge Function Active");
    </script>
</body>
</html>`;
}

serve(async (req: Request) => {
  const { url, method } = req;
  const { pathname } = new URL(url);

  if (method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Dashboard principal
    if ((pathname === '/' || pathname === '/jarvys-dashboard' || pathname === '/jarvys-dashboard/') && method === 'GET') {
      const data = getMockJarvysData();
      const html = getDashboardHTML(data);
      
      return new Response(html, {
        headers: { 
          ...corsHeaders, 
          'Content-Type': 'text/html; charset=utf-8'
        }
      });
    }

    // API Status
    if (pathname === '/api/status' && method === 'GET') {
      const data = getMockJarvysData();
      return new Response(JSON.stringify({
        ...data.status,
        edge_function: true,
        timestamp: new Date().toISOString()
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // API Metrics
    if (pathname === '/api/metrics' && method === 'GET') {
      const data = getMockJarvysData();
      return new Response(JSON.stringify({
        ...data.metrics,
        timestamp: new Date().toISOString()
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // API Complete Data
    if (pathname === '/api/data' && method === 'GET') {
      const data = getMockJarvysData();
      return new Response(JSON.stringify(data), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // API Chat
    if (pathname === '/api/chat' && method === 'POST') {
      const body = await req.json();
      const message = body.message || '';
      
      const responses = [
        `🤖 JARVYS_DEV Cloud actif ! Infrastructure sous surveillance optimale.`,
        `📊 Métriques cloud excellentes ! Coûts API optimisés et modèles performants.`,
        `🚀 Edge Function opérationnelle ! Monitoring 24/7 depuis Supabase.`,
        `💡 Suggestion: Optimisation de 15% possible sur les routes de modèles.`
      ];
      
      const response = responses[Math.floor(Math.random() * responses.length)];
      
      return new Response(JSON.stringify({ 
        response, 
        timestamp: new Date().toISOString(),
        confidence: 0.95,
        cloud: true
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Health check
    if (pathname === '/health' && method === 'GET') {
      return new Response(JSON.stringify({ 
        status: 'healthy',
        service: 'jarvys-dashboard',
        timestamp: new Date().toISOString(),
        edge_function: true
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // 404
    return new Response(JSON.stringify({ 
      error: 'Endpoint not found',
      available: ['/', '/api/status', '/api/metrics', '/api/data', '/api/chat', '/health']
    }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ 
      error: 'Internal server error',
      message: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
