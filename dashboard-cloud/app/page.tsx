"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { 
  Activity, 
  MessageCircle, 
  CheckCircle, 
  XCircle, 
  Clock,
  Github,
  Brain,
  Zap,
  AlertTriangle,
  Send
} from 'lucide-react'

interface OrchestratorStatus {
  status: 'running' | 'stopped' | 'error'
  pid?: number
  cpu_percent?: number
  memory_mb?: number
  uptime?: string
}

interface GitHubActivity {
  recent_commits: number
  recent_tasks: number
  last_activity?: string
}

interface SystemStatus {
  timestamp: string
  orchestrator: OrchestratorStatus
  github: GitHubActivity
  interface: {
    status: string
    connected_dashboards: number
  }
}

interface ChatMessage {
  id: string
  message: string
  sender: 'user' | 'orchestrator'
  timestamp: string
  status?: 'pending' | 'sent' | 'received'
}

interface Suggestion {
  id: string
  title: string
  description: string
  priority: 1 | 2 | 3
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  estimated_effort?: string
}

export default function Dashboard() {
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [logs, setLogs] = useState<string[]>([])

  // WebSocket connection pour real-time
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'ws://localhost:8000'
    const ws = new WebSocket(`${apiUrl.replace('http', 'ws')}/ws`)
    
    ws.onopen = () => {
      setIsConnected(true)
      console.log('🔌 Connecté au WebSocket JARVYS')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      switch (data.type) {
        case 'initial_status':
        case 'status_update':
          setStatus(data.data)
          break
        case 'chat_received':
          setMessages(prev => [...prev, data.data])
          break
        case 'logs_update':
          setLogs(data.data)
          break
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      console.log('🔌 Déconnecté du WebSocket JARVYS')
    }
    
    return () => ws.close()
  }, [])

  // Polling pour backup si WebSocket indisponible
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/status`)
        const data = await response.json()
        setStatus(data)
      } catch (error) {
        console.error('❌ Erreur fetch status:', error)
      }
    }

    const fetchSuggestions = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/suggestions`)
        const data = await response.json()
        setSuggestions(data.suggestions || [])
      } catch (error) {
        console.error('❌ Erreur fetch suggestions:', error)
      }
    }

    const interval = setInterval(() => {
      if (!isConnected) {
        fetchStatus()
        fetchSuggestions()
      }
    }, 10000)

    // Initial fetch
    fetchStatus()
    fetchSuggestions()

    return () => clearInterval(interval)
  }, [isConnected])

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: newMessage,
          timestamp: new Date().toISOString(),
          user_id: 'dashboard'
        })
      })

      if (response.ok) {
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          message: newMessage,
          sender: 'user',
          timestamp: new Date().toISOString(),
          status: 'sent'
        }
        setMessages(prev => [...prev, userMessage])
        setNewMessage('')
      }
    } catch (error) {
      console.error('❌ Erreur envoi message:', error)
    }
  }

  const validateSuggestion = async (suggestionId: string, action: 'approve' | 'reject', priority: number = 3) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await fetch(`${apiUrl}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_id: suggestionId,
          action,
          priority,
          comment: `${action === 'approve' ? 'Approuvé' : 'Rejeté'} depuis le dashboard`
        })
      })

      // Mettre à jour localement
      setSuggestions(prev => 
        prev.map(s => 
          s.id === suggestionId 
            ? { ...s, status: action === 'approve' ? 'approved' : 'rejected' }
            : s
        )
      )
    } catch (error) {
      console.error('❌ Erreur validation:', error)
    }
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'running': return 'text-green-500'
      case 'stopped': return 'text-red-500'
      case 'error': return 'text-yellow-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'running': return <Activity className="w-4 h-4 text-green-500 animate-pulse" />
      case 'stopped': return <XCircle className="w-4 h-4 text-red-500" />
      case 'error': return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      default: return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const getPriorityBadge = (priority: number) => {
    const variants = {
      1: 'destructive',
      2: 'default',
      3: 'secondary'
    } as const
    
    const labels = {
      1: 'High',
      2: 'Medium', 
      3: 'Low'
    }

    return <Badge variant={variants[priority as keyof typeof variants]}>{labels[priority as keyof typeof labels]}</Badge>
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Brain className="w-8 h-8 text-primary" />
            <div>
              <h1 className="text-3xl font-bold">JARVYS Dashboard</h1>
              <p className="text-muted-foreground">Orchestrateur Autonome - Monitoring & Contrôle</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-sm text-muted-foreground">
              {isConnected ? 'Connecté' : 'Déconnecté'}
            </span>
          </div>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Orchestrateur</CardTitle>
              {getStatusIcon(status?.orchestrator.status)}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold capitalize">
                {status?.orchestrator.status || 'Unknown'}
              </div>
              {status?.orchestrator.pid && (
                <p className="text-xs text-muted-foreground">
                  PID: {status.orchestrator.pid} • {status.orchestrator.uptime}
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Mémoire</CardTitle>
              <Zap className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {status?.orchestrator.memory_mb?.toFixed(1) || '0'} MB
              </div>
              <p className="text-xs text-muted-foreground">
                CPU: {status?.orchestrator.cpu_percent?.toFixed(1) || '0'}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">GitHub</CardTitle>
              <Github className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {status?.github.recent_commits || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Commits récents • {status?.github.recent_tasks || 0} tâches
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Suggestions</CardTitle>
              <MessageCircle className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {suggestions.filter(s => s.status === 'pending').length}
              </div>
              <p className="text-xs text-muted-foreground">
                En attente de validation
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="monitor" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="monitor">Monitor</TabsTrigger>
            <TabsTrigger value="chat">Chat</TabsTrigger>
            <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
          </TabsList>

          <TabsContent value="monitor" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>État Système</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status Orchestrateur</span>
                    <Badge variant={status?.orchestrator.status === 'running' ? 'default' : 'destructive'}>
                      {status?.orchestrator.status || 'Unknown'}
                    </Badge>
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <span>Dashboards Connectés</span>
                    <Badge variant="outline">
                      {status?.interface.connected_dashboards || 0}
                    </Badge>
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <span>Dernière Activité</span>
                    <span className="text-sm text-muted-foreground">
                      {status?.github.last_activity ? 
                        new Date(status.github.last_activity).toLocaleTimeString() : 
                        'Aucune'
                      }
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Métriques Performance</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Utilisation Mémoire</span>
                      <span>{status?.orchestrator.memory_mb?.toFixed(1) || '0'} MB</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ 
                          width: `${Math.min((status?.orchestrator.memory_mb || 0) / 500 * 100, 100)}%` 
                        }}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Utilisation CPU</span>
                      <span>{status?.orchestrator.cpu_percent?.toFixed(1) || '0'}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ 
                          width: `${Math.min(status?.orchestrator.cpu_percent || 0, 100)}%` 
                        }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="chat" className="space-y-4">
            <Card className="h-96">
              <CardHeader>
                <CardTitle>Chat avec JARVYS</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col h-full">
                <ScrollArea className="flex-1 pr-4">
                  <div className="space-y-4">
                    {messages.length === 0 ? (
                      <div className="text-center text-muted-foreground py-8">
                        Aucun message. Commencez une conversation avec JARVYS !
                      </div>
                    ) : (
                      messages.map((msg) => (
                        <div
                          key={msg.id}
                          className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              msg.sender === 'user'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted'
                            }`}
                          >
                            <p className="text-sm">{msg.message}</p>
                            <p className="text-xs opacity-70 mt-1">
                              {new Date(msg.timestamp).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>
                <div className="flex space-x-2 mt-4">
                  <Input
                    placeholder="Tapez votre message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  />
                  <Button onClick={sendMessage} size="icon">
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="suggestions" className="space-y-4">
            <div className="grid gap-4">
              {suggestions.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-8">
                    <MessageCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Aucune suggestion en attente</p>
                  </CardContent>
                </Card>
              ) : (
                suggestions.map((suggestion) => (
                  <Card key={suggestion.id}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0">
                      <div className="flex items-center space-x-2">
                        <CardTitle className="text-lg">{suggestion.title}</CardTitle>
                        {getPriorityBadge(suggestion.priority)}
                      </div>
                      <Badge 
                        variant={
                          suggestion.status === 'approved' ? 'default' :
                          suggestion.status === 'rejected' ? 'destructive' : 'outline'
                        }
                      >
                        {suggestion.status}
                      </Badge>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-muted-foreground">{suggestion.description}</p>
                      {suggestion.estimated_effort && (
                        <p className="text-sm text-muted-foreground">
                          Effort estimé: {suggestion.estimated_effort}
                        </p>
                      )}
                      {suggestion.status === 'pending' && (
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            onClick={() => validateSuggestion(suggestion.id, 'approve', 1)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Approuver (High)
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => validateSuggestion(suggestion.id, 'approve', 2)}
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Approuver (Medium)
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => validateSuggestion(suggestion.id, 'approve', 3)}
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Approuver (Low)
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => validateSuggestion(suggestion.id, 'reject')}
                          >
                            <XCircle className="w-4 h-4 mr-2" />
                            Rejeter
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="logs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Logs Temps Réel</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96 w-full">
                  <pre className="text-xs text-muted-foreground">
                    {logs.length === 0 ? 
                      'Aucun log disponible...' : 
                      logs.join('\n')
                    }
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
