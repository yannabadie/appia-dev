import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  email: string
  name: string
  picture: string
  accessToken: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  logout: () => void
  login: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      
      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user 
      }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      logout: () => {
        set({ user: null, isAuthenticated: false })
        localStorage.removeItem('jarvys-user')
        // Clear Google OAuth
        if (window.google?.accounts?.id) {
          window.google.accounts.id.disableAutoSelect()
        }
      },
      
      login: async (user) => {
        // Validate user email
        const AUTHORIZED_EMAILS = ['yann.abadie@gmail.com']
        
        if (!AUTHORIZED_EMAILS.includes(user.email)) {
          throw new Error('Accès non autorisé. Seul yann.abadie@gmail.com est autorisé.')
        }
        
        // Store user data
        localStorage.setItem('jarvys-user', JSON.stringify(user))
        set({ user, isAuthenticated: true })
      },
    }),
    {
      name: 'jarvys-auth',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
)
