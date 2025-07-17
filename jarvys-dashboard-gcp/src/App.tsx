import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

// Layout Components
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import CommandPalette from './components/ui/CommandPalette'

// Pages
import Dashboard from './pages/Dashboard'
import Monitor from './pages/Monitor'
import Chat from './pages/Chat'
import Tasks from './pages/Tasks'
import Settings from './pages/Settings'
import Login from './pages/Login'

// Hooks & Utils
import { useAuthStore } from './stores/authStore'
import { useThemeStore } from './stores/themeStore'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'

// Types
interface User {
  email: string
  name: string
  picture: string
  accessToken: string
}

function App() {
  const { user, isAuthenticated, setUser } = useAuthStore()
  const { theme } = useThemeStore()
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'cmd+k': () => setIsCommandPaletteOpen(true),
    'ctrl+k': () => setIsCommandPaletteOpen(true),
    'escape': () => setIsCommandPaletteOpen(false),
  })

  // Check authentication on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check for stored user session
        const storedUser = localStorage.getItem('jarvys-user')
        if (storedUser) {
          const parsedUser: User = JSON.parse(storedUser)
          
          // Validate token is still valid
          const response = await fetch('/api/auth/validate', {
            headers: {
              'Authorization': `Bearer ${parsedUser.accessToken}`
            }
          })
          
          if (response.ok) {
            setUser(parsedUser)
          } else {
            localStorage.removeItem('jarvys-user')
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        localStorage.removeItem('jarvys-user')
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [setUser])

  // Apply theme
  useEffect(() => {
    document.documentElement.className = theme
  }, [theme])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <motion.div 
          className="loading-dots"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </motion.div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <Router>
      <div className={`min-h-screen bg-background text-foreground ${theme}`}>
        {/* Grid Pattern Background */}
        <div className="fixed inset-0 grid-pattern opacity-30 pointer-events-none" />
        
        <div className="relative flex min-h-screen">
          {/* Sidebar */}
          <Sidebar />
          
          {/* Main Content */}
          <div className="flex-1 flex flex-col lg:ml-64">
            {/* Header */}
            <Header onCommandPalette={() => setIsCommandPaletteOpen(true)} />
            
            {/* Page Content */}
            <main className="flex-1 p-6 overflow-hidden">
              <AnimatePresence mode="wait">
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route 
                    path="/dashboard" 
                    element={
                      <motion.div
                        key="dashboard"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Dashboard />
                      </motion.div>
                    } 
                  />
                  <Route 
                    path="/monitor" 
                    element={
                      <motion.div
                        key="monitor"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Monitor />
                      </motion.div>
                    } 
                  />
                  <Route 
                    path="/chat" 
                    element={
                      <motion.div
                        key="chat"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Chat />
                      </motion.div>
                    } 
                  />
                  <Route 
                    path="/tasks" 
                    element={
                      <motion.div
                        key="tasks"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Tasks />
                      </motion.div>
                    } 
                  />
                  <Route 
                    path="/settings" 
                    element={
                      <motion.div
                        key="settings"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Settings />
                      </motion.div>
                    } 
                  />
                </Routes>
              </AnimatePresence>
            </main>
          </div>
        </div>

        {/* Command Palette */}
        <CommandPalette 
          isOpen={isCommandPaletteOpen}
          onClose={() => setIsCommandPaletteOpen(false)}
        />
      </div>
    </Router>
  )
}

export default App
