import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Lock, Mail } from 'lucide-react'

export default function Login() {
  const navigate = useNavigate()
  const { login, isLoading, error, clearError } = useAuthStore()
  const [email, setEmail] = useState('student1@college.com')
  const [password, setPassword] = useState('student123')
  const [loginError, setLoginError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    clearError()
    setLoginError('')

    const response = await login(email, password)
    if (response.success) {
      const role = localStorage.getItem('role')
      if (response.requires_password_change) {
        navigate('/change-password', { replace: true })
      } else {
        navigate(role === 'admin' ? '/admin' : '/student', { replace: true })
      }
    } else {
      setLoginError(response.error)
    }
  }

  return (
    <div className="min-h-screen bg-[url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=2940&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center relative">
      <div className="absolute inset-0 bg-blue-900/60 backdrop-blur-sm z-0"></div>
      
      <div className="glass-panel p-10 w-full max-w-md relative z-10 animate-[fadeIn_0.5s_ease-out]">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-gradient mb-2 tracking-tight">College Portal</h1>
          <p className="text-slate-500 font-medium text-sm uppercase tracking-widest">Academic Management</p>
        </div>

        {(loginError || error) && (
          <div className="bg-red-50/80 backdrop-blur-md border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm font-medium flex items-center">
            <span className="mr-2">⚠️</span>
            {loginError || error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-1">
            <label className="text-sm font-semibold text-slate-700 flex items-center">
              <Mail className="w-4 h-4 mr-2 text-blue-500" />
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field shadow-inner"
              placeholder="your.email@college.edu"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold text-slate-700 flex items-center">
              <Lock className="w-4 h-4 mr-2 text-blue-500" />
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
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
            {isLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Authenticating...
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-slate-500">
          <p>Mock accounts for testing:</p>
          <div className="flex justify-center gap-4 mt-2 font-medium">
            <span className="bg-slate-100 px-3 py-1 rounded-full text-slate-700">admin@college.edu</span>
            <span className="bg-slate-100 px-3 py-1 rounded-full text-slate-700">john.doe@college.edu</span>
          </div>
        </div>
      </div>
    </div>
  )
}
