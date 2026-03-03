import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'

export default function StudentDashboard() {
  const navigate = useNavigate()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const token = localStorage.getItem('token')
        if (!token) {
          navigate('/login')
          return
        }

        const response = await api.get('/student/dashboard')
        console.log('Dashboard Response:', response.data)
        setDashboardData(response.data)
      } catch (err) {
        console.error('Error fetching dashboard:', err?.response?.data || err.message)
        setError(err?.response?.data?.detail || err.message || 'Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [navigate])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-700">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  if (error || !dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <h2 className="text-xl font-bold text-red-600 mb-4">Error Loading Dashboard</h2>
          <p className="text-gray-700 mb-6">{error || 'Student data not found'}</p>
          <div className="space-y-3">
            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Retry
            </button>
            <button
              onClick={() => {
                localStorage.clear()
                navigate('/login')
              }}
              className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    )
  }

  const getYearLabel = (year) => {
    const labels = ['', '1st Year', '2nd Year', '3rd Year', '4th Year']
    return labels[year] || `Year ${year}`
  }

  const stats = [
    {
      label: 'Attendance',
      value: `${(dashboardData?.attendance?.attendance_percentage || 0).toFixed(1)}%`,
      icon: '📊',
      color: 'blue',
    },
    {
      label: 'GPA',
      value: (dashboardData?.progress?.gpa || 0).toFixed(2),
      icon: '⭐',
      color: 'green',
    },
    {
      label: 'Assignments',
      value: dashboardData?.progress?.total_assignments_completed || 0,
      icon: '✅',
      color: 'orange',
    },
    {
      label: 'Quizzes',
      value: dashboardData?.progress?.total_quizzes_attempted || 0,
      icon: '🧠',
      color: 'purple',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              👋 Welcome, {dashboardData?.name}!
            </h1>
            <p className="text-gray-600 mt-1">
              {dashboardData?.department} • {getYearLabel(dashboardData?.current_year)} • Batch {dashboardData?.batch_year}
            </p>
          </div>
          <button
            onClick={() => {
              localStorage.clear()
              navigate('/login')
            }}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {stats.map((stat) => (
            <div key={stat.label} className="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">{stat.label}</p>
                  <p className={`text-3xl font-bold text-${stat.color}-600 mt-2`}>
                    {stat.value}
                  </p>
                </div>
                <div className="text-4xl">{stat.icon}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="flex flex-wrap border-b overflow-x-auto">
            {[
              { id: 'overview', label: '📋 Overview' },
              { id: 'assignments', label: '✍️ Assignments' },
              { id: 'quizzes', label: '🧪 Quizzes' },
              { id: 'materials', label: '📚 Study Materials' },
              { id: 'attendance', label: '📍 Attendance' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-medium whitespace-nowrap transition ${
                  activeTab === tab.id
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Notifications */}
                <div className="lg:col-span-2">
                  <h2 className="text-xl font-bold mb-4">📬 Notifications</h2>
                  <div className="space-y-3">
                    {dashboardData?.notifications?.length > 0 ? (
                      dashboardData.notifications.map((notif) => (
                        <div
                          key={notif.id}
                          className="p-4 bg-blue-50 border-l-4 border-blue-600 rounded-r-lg"
                        >
                          <h3 className="font-semibold text-gray-900">{notif.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(notif.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 text-center py-6">No notifications</p>
                    )}
                  </div>
                </div>

                {/* Summary Card */}
                <div className="bg-gradient-to-br from-blue-600 to-blue-800 text-white rounded-lg p-6">
                  <h2 className="text-xl font-bold mb-4">📊 Academic Summary</h2>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span>Current Year:</span>
                      <span className="font-bold">{getYearLabel(dashboardData?.current_year)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Department:</span>
                      <span className="font-bold">{dashboardData?.department}</span>
                    </div>
                    <div className="flex justify-between pt-3 border-t border-blue-400">
                      <span>Attendance:</span>
                      <span className="font-bold">
                        {(dashboardData?.attendance?.attendance_percentage || 0).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Overall GPA:</span>
                      <span className="font-bold">
                        {(dashboardData?.progress?.gpa || 0).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Assignments Tab */}
            {activeTab === 'assignments' && (
              <div>
                <h2 className="text-xl font-bold mb-4">✍️ My Assignments</h2>
                <div className="space-y-4">
                  {dashboardData?.assignments?.length > 0 ? (
                    dashboardData.assignments.map((assignment) => (
                      <div
                        key={assignment.id}
                        className="bg-white border rounded-lg p-4 hover:shadow-md transition"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-bold text-gray-900">
                              {assignment.title}
                            </h3>
                            <p className="text-sm text-gray-600">
                              {assignment.subject_name}
                            </p>
                          </div>
                          <span className="px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-semibold">
                            {assignment.status?.toUpperCase() || 'PENDING'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">
                          {assignment.description}
                        </p>
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-600">
                            Due: {new Date(assignment.due_date).toLocaleDateString()}
                          </span>
                          <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                            View
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-center py-8">No assignments</p>
                  )}
                </div>
              </div>
            )}

            {/* Quizzes Tab */}
            {activeTab === 'quizzes' && (
              <div>
                <h2 className="text-xl font-bold mb-4">🧪 My Quizzes</h2>
                <div className="space-y-4">
                  {dashboardData?.quizzes?.length > 0 ? (
                    dashboardData.quizzes.map((quiz) => (
                      <div
                        key={quiz.id}
                        className="bg-white border rounded-lg p-4 hover:shadow-md transition"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-bold text-gray-900">{quiz.title}</h3>
                            <p className="text-sm text-gray-600">{quiz.subject_name}</p>
                          </div>
                          <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-semibold">
                            {quiz.duration_minutes} mins
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{quiz.description}</p>
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-600">
                            Marks: {quiz.max_marks}
                          </span>
                          <button className="px-4 py-2 bg-purple-600 text-white text-sm rounded hover:bg-purple-700">
                            Start Quiz
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-center py-8">No quizzes</p>
                  )}
                </div>
              </div>
            )}

            {/* Study Materials Tab */}
            {activeTab === 'materials' && (
              <div>
                <h2 className="text-xl font-bold mb-4">
                  📚 {getYearLabel(dashboardData?.current_year)} Study Materials
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {dashboardData?.academic_content?.length > 0 ? (
                    dashboardData.academic_content.map((content) => (
                      <a
                        key={content.id}
                        href={content.file_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border rounded-lg hover:shadow-lg transition"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-bold text-gray-900 text-sm">
                              {content.title}
                            </h3>
                            <p className="text-xs text-gray-600 mt-1">
                              {content.subject_name}
                            </p>
                            <span className="inline-block mt-2 px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded capitalize">
                              {content.content_type}
                            </span>
                          </div>
                          <span className="text-2xl">📖</span>
                        </div>
                      </a>
                    ))
                  ) : (
                    <p className="text-gray-500 text-center py-8 col-span-full">
                      No study materials yet
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Attendance Tab */}
            {activeTab === 'attendance' && (
              <div>
                <h2 className="text-xl font-bold mb-4">📍 Attendance Summary</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-6 border">
                    <p className="text-gray-600 text-sm mb-2">Overall Attendance</p>
                    <p className="text-4xl font-bold text-green-600">
                      {(dashboardData?.attendance?.attendance_percentage || 0).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-6 border">
                    <p className="text-gray-600 text-sm mb-2">Classes Attended</p>
                    <p className="text-4xl font-bold text-blue-600">
                      {dashboardData?.attendance?.classes_attended || 0}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-lg p-6 border">
                    <p className="text-gray-600 text-sm mb-2">Total Classes</p>
                    <p className="text-4xl font-bold text-orange-600">
                      {dashboardData?.attendance?.total_classes || 0}
                    </p>
                  </div>
                </div>

                {dashboardData?.consolidated_marks?.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-lg font-bold mb-4">📈 Recent Marks</h3>
                    <div className="overflow-x-auto rounded-lg border">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-100">
                          <tr>
                            <th className="px-4 py-2 text-left font-semibold">Subject</th>
                            <th className="px-4 py-2 text-left font-semibold">Assessment</th>
                            <th className="px-4 py-2 text-left font-semibold">Marks</th>
                          </tr>
                        </thead>
                        <tbody>
                          {dashboardData.consolidated_marks.map((mark, idx) => (
                            <tr key={idx} className="border-t hover:bg-gray-50">
                              <td className="px-4 py-2">{mark.subject_name}</td>
                              <td className="px-4 py-2">{mark.assessment_name}</td>
                              <td className="px-4 py-2 font-bold">
                                {mark.marks_obtained} / {mark.max_marks}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
