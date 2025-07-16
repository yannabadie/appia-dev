import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Shield, Zap, Globe } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: any) => void
          renderButton: (element: HTMLElement, config: any) => void
          prompt: () => void
          disableAutoSelect: () => void
        }
      }
    }
  }
}

export default function Login() {
  const { login, setLoading, isLoading } = useAuthStore()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Load Google Identity Services
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    
    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          callback: handleCredentialResponse,
          auto_select: false,
          cancel_on_tap_outside: false,
        })

        // Render the sign-in button
        const buttonElement = document.getElementById('google-signin-button')
        if (buttonElement) {
          window.google.accounts.id.renderButton(buttonElement, {
            theme: 'outline',
            size: 'large',
            type: 'standard',
            text: 'signin_with',
            width: 300,
            logo_alignment: 'left'
          })
        }
      }
    }

    document.head.appendChild(script)

    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script)
      }
    }
  }, [])

  const handleCredentialResponse = async (response: any) => {
    try {
      setLoading(true)
      setError(null)

      // Decode the JWT token
      const credential = response.credential
      const payload = JSON.parse(atob(credential.split('.')[1]))
      
      const user = {
        email: payload.email,
        name: payload.name,
        picture: payload.picture,
        accessToken: credential
      }

      await login(user)
    } catch (error: any) {
      setError(error.message || 'Erreur de connexion')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted flex items-center justify-center p-4">
      {/* Background Grid */}
      <div className="fixed inset-0 grid-pattern opacity-20" />
      
      {/* Floating Neural Network Effect */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-jarvys-primary rounded-full"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              opacity: 0
            }}
            animate={{
              y: [null, -100, -200],
              opacity: [0, 0.6, 0]
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 5
            }}
          />
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative w-full max-w-md"
      >
        {/* Main Login Card */}
        <div className="glass rounded-2xl p-8 shadow-2xl border">
          {/* Logo & Branding */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-jarvys-primary to-jarvys-neural rounded-2xl mb-4 neural-glow"
            >
              <Brain className="w-8 h-8 text-black" />
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-3xl font-bold gradient-text mb-2"
            >
              JARVYS Dashboard
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="text-muted-foreground"
            >
              Orchestrateur Autonome - Interface de Contrôle
            </motion.p>
          </div>

          {/* Features Showcase */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="grid grid-cols-3 gap-4 mb-8"
          >
            <div className="text-center">
              <div className="w-12 h-12 bg-jarvys-primary/10 rounded-xl flex items-center justify-center mx-auto mb-2">
                <Zap className="w-6 h-6 text-jarvys-primary" />
              </div>
              <p className="text-xs text-muted-foreground">Real-time</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-jarvys-neural/10 rounded-xl flex items-center justify-center mx-auto mb-2">
                <Shield className="w-6 h-6 text-jarvys-neural" />
              </div>
              <p className="text-xs text-muted-foreground">Sécurisé</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-jarvys-accent/10 rounded-xl flex items-center justify-center mx-auto mb-2">
                <Globe className="w-6 h-6 text-jarvys-accent" />
              </div>
              <p className="text-xs text-muted-foreground">Cloud</p>
            </div>
          </motion.div>

          {/* Google Sign-In */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="space-y-4"
          >
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-4">
                Connectez-vous avec votre compte autorisé
              </p>
              
              <div 
                id="google-signin-button" 
                className="flex justify-center"
              />
              
              {isLoading && (
                <div className="mt-4 flex items-center justify-center">
                  <div className="loading-dots scale-50">
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                  </div>
                </div>
              )}
              
              {error && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg"
                >
                  <p className="text-sm text-destructive">{error}</p>
                </motion.div>
              )}
            </div>
          </motion.div>

          {/* Security Notice */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="mt-8 pt-6 border-t border-border"
          >
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Shield className="w-4 h-4" />
              <span>Accès restreint à yann.abadie@gmail.com</span>
            </div>
          </motion.div>
        </div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4 }}
          className="text-center mt-8"
        >
          <p className="text-xs text-muted-foreground">
            Propulsé par{' '}
            <span className="text-jarvys-primary font-medium">
              Google Cloud Platform
            </span>
            {' '}• Sécurisé par{' '}
            <span className="text-jarvys-neural font-medium">
              OAuth 2.0
            </span>
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}
