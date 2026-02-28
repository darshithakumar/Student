import React, { useState, useEffect } from 'react'
import { adminAPI } from '../../api/client'
import { Users, FileText, CheckSquare, BarChart3 } from 'lucide-react'

export default function AdminHome() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminAPI.getDashboard()
      .then((res) => {
        setStats(res.data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>
  }

  const statCards = [
    {
      label: 'Total Students',
      value: stats?.total_students || 0,
      icon: Users,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      label: 'Assignments',
      value: stats?.total_assignments || 0,
      icon: FileText,
      color: 'bg-orange-100 text-orange-600',
    },
    {
      label: 'Quizzes',
      value: stats?.total_quizzes || 0,
      icon: CheckSquare,
      color: 'bg-purple-100 text-purple-600',
    },
    {
      label: 'Avg Attendance',
      value: `${stats?.average_attendance?.toFixed(1)}%` || 'N/A',
      icon: BarChart3,
      color: 'bg-green-100 text-green-600',
    },
  ]

  return (
    <div>
      <h1 className="text-4xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
      <p className="text-gray-600 mb-8">System overview and management</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
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
    </div>
  )
}
