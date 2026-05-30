import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function ProtectedRoute({ children, requiredRole }) {
  const { token, user } = useAuthStore()

  if (!token) {
    return <Navigate to="/login" replace />
  }

  // During token validation (page refresh), user may not be set yet
  // Use localStorage role as fallback to prevent redirect flash
  const role = user?.role || localStorage.getItem('role')

  if (requiredRole && role !== requiredRole) {
    // If user is not yet loaded but token exists, show loading
    if (!user && token) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Verifying session...</p>
          </div>
        </div>
      )
    }
    return <Navigate to="/login" replace />
  }

  return children
}
