import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../api/client'
import { Lock } from 'lucide-react'

export default function ChangePassword() {
  const navigate = useNavigate()
  const { token, user } = useAuthStore()
  
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Only allow if logged in and requires password change
    if (!token) {
      navigate('/login')
    }
  }, [token, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters long')
      return
    }

    setIsLoading(true)
    try {
      await authAPI.changePassword(token, newPassword)
      localStorage.removeItem('requires_password_change')
      
      const role = localStorage.getItem('role')
      navigate(role === 'admin' ? '/admin' : '/student', { replace: true })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to change password')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=2940&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center relative">
      <div className="absolute inset-0 bg-blue-900/60 backdrop-blur-sm z-0"></div>
      
      <div className="glass-panel p-10 w-full max-w-md relative z-10 animate-[fadeIn_0.5s_ease-out]">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-extrabold text-gradient mb-2 tracking-tight">Security Update</h1>
          <p className="text-slate-200 font-medium text-sm">Please set a new personal password to secure your account.</p>
        </div>

        {error && (
          <div className="bg-red-50/80 backdrop-blur-md border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm font-medium flex items-center">
            <span className="mr-2">⚠️</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-1">
            <label className="text-sm font-semibold text-slate-700 flex items-center">
              <Lock className="w-4 h-4 mr-2 text-blue-500" />
              New Password
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="input-field shadow-inner"
              placeholder="••••••••"
              required
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-semibold text-slate-700 flex items-center">
              <Lock className="w-4 h-4 mr-2 text-blue-500" />
              Confirm Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="input-field shadow-inner"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-primary py-3 text-lg mt-4 disabled:opacity-50 disabled:cursor-not-allowed group flex justify-center items-center"
          >
            {isLoading ? 'Updating...' : 'Secure Account'}
          </button>
        </form>
      </div>
    </div>
  )
}
