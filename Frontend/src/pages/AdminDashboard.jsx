import React, { useState, useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import { LogOut, Menu, X } from 'lucide-react'
import { adminAPI } from '../api/client'
import { useAuthStore } from '../store/authStore'
import AdminHome from '../pages/admin/Home'
import AdminStudents from '../pages/admin/Students'
import AdminAttendance from '../pages/admin/Attendance'
import AdminMarks from '../pages/admin/Marks'
import AdminAssignments from '../pages/admin/Assignments'
import AdminLogs from '../pages/admin/Logs'

export default function AdminDashboard() {
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const menuItems = [
    { label: 'Dashboard', path: '', icon: '📊' },
    { label: 'Students', path: 'students', icon: '👥' },
    { label: 'Attendance', path: 'attendance', icon: '✓' },
    { label: 'Marks', path: 'marks', icon: '📈' },
    { label: 'Assignments', path: 'assignments', icon: '📝' },
    { label: 'Admin Logs', path: 'logs', icon: '📋' },
  ]

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-0'} bg-gray-900 text-white transition-all duration-300 overflow-hidden`}>
        <div className="p-6">
          <h2 className="text-2xl font-bold">Portal</h2>
          <p className="text-gray-400 text-sm">Administrator</p>
        </div>

        <nav className="mt-8">
          {menuItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className="w-full flex items-center px-6 py-3 text-left hover:bg-gray-800 transition"
            >
              <span className="mr-3 text-xl">{item.icon}</span>
              <span>{item.label}</span>
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
            <Route index element={<AdminHome />} />
            <Route path="students" element={<AdminStudents />} />
            <Route path="attendance" element={<AdminAttendance />} />
            <Route path="marks" element={<AdminMarks />} />
            <Route path="assignments" element={<AdminAssignments />} />
            <Route path="logs" element={<AdminLogs />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
