import React, { useState, useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import { LogOut, Menu, X } from 'lucide-react'
import { studentAPI } from '../api/client'
import { useAuthStore } from '../store/authStore'
import StudentHome from '../pages/student/Home'
import StudentAssignments from '../pages/student/Assignments'
import StudentQuizzes from '../pages/student/Quizzes'
import StudentAttendance from '../pages/student/Attendance'
import StudentMarks from '../pages/student/Marks'
import StudentNotifications from '../pages/student/Notifications'
import StudentTodos from '../pages/student/Todos'

export default function StudentDashboard() {
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [notificationCount, setNotificationCount] = useState(0)

  useEffect(() => {
    // Fetch unread notifications count
    studentAPI.getNotifications(true)
      .then((response) => {
        setNotificationCount(response.data.total)
      })
      .catch(() => {})
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const menuItems = [
    { label: 'Dashboard', path: '', icon: '📊' },
    { label: 'Assignments', path: 'assignments', icon: '📝' },
    { label: 'Quizzes', path: 'quizzes', icon: '❓' },
    { label: 'Attendance', path: 'attendance', icon: '✓' },
    { label: 'Marks', path: 'marks', icon: '📈' },
    { label: 'Notifications', path: 'notifications', icon: '🔔', badge: notificationCount },
    { label: 'Todos', path: 'todos', icon: '✓' },
  ]

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-0'} bg-gray-900 text-white transition-all duration-300 overflow-hidden`}>
        <div className="p-6">
          <h2 className="text-2xl font-bold">Portal</h2>
          <p className="text-gray-400 text-sm">Student</p>
        </div>

        <nav className="mt-8">
          {menuItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className="w-full flex items-center px-6 py-3 text-left hover:bg-gray-800 transition"
            >
              <span className="mr-3 text-xl">{item.icon}</span>
              <span className="flex-1">{item.label}</span>
              {item.badge > 0 && (
                <span className="bg-red-600 text-white text-xs px-2 py-1 rounded-full">
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        <button
          onClick={handleLogout}
          className="w-full flex items-center px-6 py-3 text-left hover:bg-red-900 transition mt-8 border-t border-gray-800"
        >
          <LogOut className="mr-3 w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="text-gray-600 hover:text-gray-900"
          >
            {isSidebarOpen ? <X /> : <Menu />}
          </button>
          
          <div className="flex items-center space-x-4">
            <span className="text-gray-700 font-medium">{user?.email}</span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route index element={<StudentHome />} />
            <Route path="assignments" element={<StudentAssignments />} />
            <Route path="quizzes" element={<StudentQuizzes />} />
            <Route path="attendance" element={<StudentAttendance />} />
            <Route path="marks" element={<StudentMarks />} />
            <Route path="notifications" element={<StudentNotifications />} />
            <Route path="todos" element={<StudentTodos />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
