import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Lock, Mail, Key } from 'lucide-react'
import { authAPI } from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const { login, isLoading, error, clearError } = useAuthStore()
  const [email, setEmail] = useState('student1@college.com')
  const [password, setPassword] = useState('student123')
  const [loginError, setLoginError] = useState('')
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isChanging, setIsChanging] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    clearError()
    setLoginError('')

    const response = await login(email, password)
    if (response.success) {
      if (response.requires_password_change) {
        setShowChangePassword(true)
      } else {
        const role = localStorage.getItem('role')
        navigate(role === 'admin' ? '/admin' : '/student', { replace: true })
      }
    } else {
      setLoginError(response.error)
    }
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    setLoginError('')
    
    if (newPassword !== confirmPassword) {
      setLoginError("New passwords don't match")
      return
    }

    setIsChanging(true)
    try {
      const userId = localStorage.getItem('user_id')
      await authAPI.changePassword({
        user_id: userId,
        old_password: password,
        new_password: newPassword
      })
      // Password changed successfully, proceed to dashboard
      const role = localStorage.getItem('role')
      navigate(role === 'admin' ? '/admin' : '/student', { replace: true })
    } catch (err) {
      setLoginError(err.response?.data?.detail || "Failed to change password")
    } finally {
      setIsChanging(false)
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

        {!showChangePassword ? (
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
        ) : (
          <form onSubmit={handleChangePassword} className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-xl p-4 text-sm font-medium mb-4">
              <p>Welcome! Since this is your first time logging in, you must change your password to continue.</p>
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-700 flex items-center">
                <Key className="w-4 h-4 mr-2 text-blue-500" />
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="input-field shadow-inner"
                placeholder="Enter new password"
                required
                minLength={8}
              />
            </div>

            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-700 flex items-center">
                <Lock className="w-4 h-4 mr-2 text-blue-500" />
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input-field shadow-inner"
                placeholder="Confirm new password"
                required
                minLength={8}
              />
            </div>

            <button
              type="submit"
              disabled={isChanging}
              className="w-full btn-primary py-3 text-lg mt-4 disabled:opacity-50 disabled:cursor-not-allowed group flex justify-center items-center"
            >
              {isChanging ? 'Changing Password...' : 'Save & Continue'}
            </button>
          </form>
        )}

        <div className="mt-8 text-center text-sm text-slate-500">
          <p>Mock accounts for testing:</p>
          <div className="flex flex-col items-center justify-center gap-2 mt-2 font-medium">
            <span className="bg-slate-100 px-3 py-1 rounded-full text-slate-700 text-xs w-full max-w-xs">Admin: admin@college.edu / admin123</span>
            <span className="bg-slate-100 px-3 py-1 rounded-full text-slate-700 text-xs w-full max-w-xs">Student: john.doe@college.edu / student123</span>
            <span className="bg-green-50 border border-green-200 px-3 py-1 rounded-full text-green-700 text-xs w-full max-w-xs mt-2">New: vvce23cse0001@vvce.ac.in / VvceStudent@123</span>
          </div>
        </div>
      </div>
    </div>
  )
}
