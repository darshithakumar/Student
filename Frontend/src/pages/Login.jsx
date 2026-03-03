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
      navigate(role === 'admin' ? '/admin' : '/student', { replace: true })
    } else {
      setLoginError(response.error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-900 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">College Portal</h1>
          <p className="text-gray-600 mt-2">Academic Management System</p>
        </div>

        {(loginError || error) && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {loginError || error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Mail className="inline mr-2 w-4 h-4" />
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              placeholder="your.email@college.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Lock className="inline mr-2 w-4 h-4" />
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg text-sm text-gray-700">
          <p className="font-semibold mb-2">📝 Test Credentials:</p>
          <p className="mb-3"><strong>👨‍💼 Admin:</strong></p>
          <p className="ml-4">Email: admin@college.com</p>
          <p className="ml-4 mb-3">Password: admin123</p>
          <p><strong>👨‍🎓 Student:</strong></p>
          <p className="ml-4">Email: student1@college.com</p>
          <p className="ml-4">Password: student123</p>
        </div>
      </div>
    </div>
  )
}
