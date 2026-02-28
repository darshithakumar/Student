import { create } from 'zustand'
import { authAPI } from '../api/client'

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('token') || null,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authAPI.login(email, password)
      const { access_token, user_id, role } = response.data
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('user_id', user_id)
      localStorage.setItem('role', role)

      set({
        token: access_token,
        user: { id: user_id, email, role },
        isLoading: false,
      })

      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed'
      set({ error: message, isLoading: false })
      return { success: false, error: message }
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authAPI.register(data)
      set({ isLoading: false })
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed'
      set({ error: message, isLoading: false })
      return { success: false, error: message }
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('role')
    set({ user: null, token: null })
  },

  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  clearError: () => set({ error: null }),
}))
