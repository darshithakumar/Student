import React, { useState, useEffect } from 'react'
import { studentAPI } from '../../api/client'
import { BookOpen, FileText, CheckSquare, BarChart3 } from 'lucide-react'

export default function StudentHome() {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    studentAPI.getDashboard()
      .then((response) => {
        setDashboard(response.data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load dashboard')
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>
  }

  if (error) {
    return <div className="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
  }

  if (!dashboard) {
    return <div className="text-center py-12">No dashboard data available</div>
  }

  const stats = [
    {
      label: 'Current Year',
      value: dashboard.current_year,
      icon: BookOpen,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      label: 'GPA',
      value: dashboard.progress?.gpa?.toFixed(2) || 'N/A',
      icon: BarChart3,
      color: 'bg-green-100 text-green-600',
    },
    {
      label: 'Attendance',
      value: `${dashboard.attendance?.attendance_percentage?.toFixed(1)}%` || 'N/A',
      icon: CheckSquare,
      color: 'bg-purple-100 text-purple-600',
    },
    {
      label: 'Assignments',
      value: dashboard.progress?.total_assignments_completed || 0,
      icon: FileText,
      color: 'bg-orange-100 text-orange-600',
    },
  ]

  return (
    <div>
      <h1 className="text-4xl font-bold text-gray-900 mb-2">Welcome, {dashboard.name}!</h1>
      <p className="text-gray-600 mb-8">{dashboard.department} - Year {dashboard.current_year}</p>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className="card">
              <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                <Icon className="w-6 h-6" />
              </div>
              <p className="text-gray-600 text-sm">{stat.label}</p>
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
            </div>
          )
        })}
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Academic Content */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">📚 Academic Materials</h2>
          {dashboard.academic_content?.notes?.length > 0 ? (
            <ul className="space-y-2">
              {dashboard.academic_content.notes.slice(0, 3).map((note) => (
                <li key={note.id} className="text-sm text-gray-700">
                  • {note.title}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No materials available</p>
          )}
        </div>

        {/* Pending Assignments */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">📝 Pending Assignments</h2>
          {dashboard.assignments?.filter(a => a.status === 'pending').length > 0 ? (
            <ul className="space-y-2">
              {dashboard.assignments.filter(a => a.status === 'pending').slice(0, 3).map((assign) => (
                <li key={assign.id} className="text-sm">
                  <p className="font-medium text-gray-900">{assign.title}</p>
                  <p className="text-gray-600">Due: {new Date(assign.due_date).toLocaleDateString()}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No pending assignments</p>
          )}
        </div>

        {/* Recent Notifications */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🔔 Recent Notifications</h2>
          {dashboard.notifications?.length > 0 ? (
            <ul className="space-y-2">
              {dashboard.notifications.slice(0, 3).map((notif) => (
                <li key={notif.id} className="text-sm">
                  <p className="font-medium text-gray-900">{notif.title}</p>
                  <p className="text-gray-600 text-xs">{new Date(notif.created_at).toLocaleDateString()}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No notifications</p>
          )}
        </div>

        {/* Consolidated Marks */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">📊 Consolidated Marks</h2>
          {dashboard.consolidated_marks ? (
            <div>
              <p className="text-3xl font-bold text-gray-900">
                {dashboard.consolidated_marks.overall_percentage?.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">Out of 100</p>
            </div>
          ) : (
            <p className="text-gray-500">No marks data</p>
          )}
        </div>
      </div>
    </div>
  )
}
