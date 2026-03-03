import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import StudentDashboard from './pages/student/SimpleStudentDashboard'
import AdminDashboard from './pages/admin/CompleteAdminDashboard'
import { authAPI } from './api/client'

function App() {
  const { setUser, setToken } = useAuthStore()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Validate token on app load
      authAPI.validateToken(token)
        .then((response) => {
          if (response.data.valid) {
            setToken(token)
            setUser({
              id: response.data.user_id,
              email: response.data.email,
              role: response.data.role,
            })
          }
        })
        .catch(() => {
          localStorage.removeItem('token')
        })
    }
  }, [setUser, setToken])

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route
          path="/student/*"
          element={
            <ProtectedRoute requiredRole="student">
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  )
}

export default App
