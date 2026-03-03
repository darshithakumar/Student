import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/client'

export default function StudentDashboard() {
  const navigate = useNavigate()
  const [student, setStudent] = useState(null)
  const [academicContent, setAcademicContent] = useState([])
  const [assignments, setAssignments] = useState([])
  const [quizzes, setQuizzes] = useState([])
  const [attendance, setAttendance] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [todos, setTodos] = useState([])
  const [progress, setProgress] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [newTodo, setNewTodo] = useState('')
  const [showAiAssistant, setShowAiAssistant] = useState(false)

  // Calculate current year based on batch year
  const getCurrentYear = (batchYear) => {
    const currentYear = new Date().getFullYear()
    const yearOfStudy = currentYear - batchYear + 1
    if (yearOfStudy < 1) return 1
    if (yearOfStudy > 4) return 4
    return yearOfStudy
  }

  // Fetch all student data
  useEffect(() => {
    const fetchStudentData = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          navigate('/login')
          return
        }

        // Get student dashboard/profile
        const dashboardRes = await api.get('/student/dashboard')
        const studentData = dashboardRes.data
        setStudent(studentData)

        // Get assignments for student
        const assignmentsRes = await api.get('/student/assignments')
        setAssignments(assignmentsRes.data || [])

        // Get quizzes for student
        const quizzesRes = await api.get('/student/quizzes')
        setQuizzes(quizzesRes.data || [])

        // Get attendance
        const attendanceRes = await api.get('/student/attendance')
        setAttendance(attendanceRes.data)

        // Get notifications
        const notificationsRes = await api.get('/student/notifications')
        setNotifications(notificationsRes.data || [])

        // Get todos
        const todosRes = await api.get('/student/todos')
        setTodos(todosRes.data || [])

        setLoading(false)
      } catch (error) {
        console.error('Error fetching student data:', error)
        setLoading(false)
      }
    }

    fetchStudentData()
  }, [navigate])

  const handleAddTodo = async () => {
    if (newTodo.trim()) {
      try {
        const response = await api.post('/student/todos', {
          title: newTodo,
          completed: false,
        })
        setTodos([...todos, response.data])
        setNewTodo('')
      } catch (error) {
        console.error('Error adding todo:', error)
      }
    }
  }

  const handleToggleTodo = async (todoId) => {
    try {
      const todo = todos.find(t => t.id === todoId)
      const response = await api.patch(`/student/todos/${todoId}`, {
        completed: !todo.completed,
      })
      setTodos(todos.map(t => (t.id === todoId ? response.data : t)))
    } catch (error) {
      console.error('Error updating todo:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  if (!student) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2>Failed to load student data</h2>
          <button
            onClick={() => navigate('/login')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
          >
            Logout
          </button>
        </div>
      </div>
    )
  }

  const currentYear = getCurrentYear(student.batch_year)
  const yearName = ['', '1st Year', '2nd Year', '3rd Year', '4th Year'][currentYear]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome, {student.name}! 👋
            </h1>
            <p className="text-gray-600 mt-1">
              {student.department} • {yearName} • Batch {student.batch_year}
            </p>
          </div>
          <button
            onClick={() => {
              localStorage.clear()
              navigate('/login')
            }}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Attendance</p>
                <p className="text-3xl font-bold text-blue-600">
                  {attendance?.attendance_percentage.toFixed(1)}%
                </p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">GPA</p>
                <p className="text-3xl font-bold text-green-600">
                  {progress?.gpa.toFixed(2)}
                </p>
              </div>
              <div className="text-4xl">⭐</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Assignments Done</p>
                <p className="text-3xl font-bold text-orange-600">
                  {progress?.total_assignments_completed}
                </p>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Quizzes Done</p>
                <p className="text-3xl font-bold text-purple-600">
                  {progress?.total_quizzes_attempted}
                </p>
              </div>
              <div className="text-4xl">🧠</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="flex flex-wrap gap-2 p-4 border-b">
            {[
              { id: 'overview', label: '📋 Overview', icon: '📋' },
              { id: 'materials', label: '📚 Study Materials', icon: '📚' },
              { id: 'assignments', label: '✍️ My Assignments', icon: '✍️' },
              { id: 'quizzes', label: '🧪 My Quizzes', icon: '🧪' },
              { id: 'attendance', label: '📍 Attendance', icon: '📍' },
              { id: 'marks', label: '📈 Marks', icon: '📈' },
              { id: 'todos', label: '✓ My Tasks', icon: '✓' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Notifications */}
              <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">📬 Notifications</h2>
                {notifications.length === 0 ? (
                  <p className="text-gray-500">No notifications</p>
                ) : (
                  <div className="space-y-3">
                    {notifications.map(notif => (
                      <div
                        key={notif.id}
                        className="p-3 bg-blue-50 border-l-4 border-blue-600 rounded"
                      >
                        <h3 className="font-semibold text-gray-900">
                          {notif.title}
                        </h3>
                        <p className="text-sm text-gray-600">{notif.message}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(notif.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Quick Stats */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">⚡ Quick Stats</h2>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-amber-50 rounded">
                    <span className="text-sm text-gray-700">Pending Assignments</span>
                    <span className="font-bold text-amber-600">
                      {assignments.filter(a => a.status === 'pending').length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-purple-50 rounded">
                    <span className="text-sm text-gray-700">Active Quizzes</span>
                    <span className="font-bold text-purple-600">
                      {quizzes.filter(q => new Date(q.end_time) > new Date()).length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                    <span className="text-sm text-gray-700">Classes Today</span>
                    <span className="font-bold text-green-600">
                      {attendance?.month === new Date().getMonth() + 1 ? attendance.total_classes : 0}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Study Materials Tab */}
          {activeTab === 'materials' && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold mb-4">
                  📚 {yearName} Study Materials
                </h2>
                <p className="text-gray-600 mb-6">
                  All materials matched to your current academic level
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {['Notes', 'PPT', 'Textbooks', 'PYQs', 'Demo Test', 'Solutions'].map(
                  type => (
                    <div
                      key={type}
                      className="bg-white rounded-lg shadow hover:shadow-lg transition p-6 cursor-pointer"
                    >
                      <div className="text-4xl mb-3">
                        {type === 'Notes' && '📝'}
                        {type === 'PPT' && '🎥'}
                        {type === 'Textbooks' && '📖'}
                        {type === 'PYQs' && '❓'}
                        {type === 'Demo Test' && '🧪'}
                        {type === 'Solutions' && '✅'}
                      </div>
                      <h3 className="text-lg font-bold mb-2">{type}</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Access your {type.toLowerCase()} for {yearName}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {academicContent
                          .filter(
                            c =>
                              c.content_type.toLowerCase() ===
                              type.toLowerCase()
                          )
                          .map(content => (
                            <a
                              key={content.id}
                              href={content.file_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                            >
                              {content.subject_name}
                            </a>
                          ))}
                      </div>
                    </div>
                  )
                )}
              </div>

              {academicContent.length === 0 && (
                <div className="bg-yellow-50 border-l-4 border-yellow-600 p-6 rounded">
                  <p className="text-yellow-800">
                    📦 No study materials uploaded yet for {yearName}. Check back
                    soon!
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Assignments Tab */}
          {activeTab === 'assignments' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">✍️ My Assignments</h2>
              <div className="space-y-4">
                {assignments.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    No assignments yet
                  </p>
                ) : (
                  assignments.map(assignment => (
                    <div
                      key={assignment.id}
                      className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="text-lg font-bold">{assignment.title}</h3>
                          <p className="text-sm text-gray-600">
                            {assignment.subject_name}
                          </p>
                        </div>
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-semibold ${
                            assignment.status === 'submitted'
                              ? 'bg-green-100 text-green-800'
                              : assignment.status === 'graded'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-orange-100 text-orange-800'
                          }`}
                        >
                          {assignment.status.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-700 mb-4">{assignment.description}</p>
                      <div className="flex justify-between items-center">
                        <div className="text-sm text-gray-600">
                          Due: {new Date(assignment.due_date).toLocaleDateString()}
                        </div>
                        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                          {assignment.status === 'pending' ? 'Submit' : 'View Feedback'}
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Quizzes Tab */}
          {activeTab === 'quizzes' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">🧪 My Quizzes</h2>
              <div className="space-y-4">
                {quizzes.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No quizzes yet</p>
                ) : (
                  quizzes.map(quiz => (
                    <div
                      key={quiz.id}
                      className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="text-lg font-bold">{quiz.title}</h3>
                          <p className="text-sm text-gray-600">
                            {quiz.subject_name}
                          </p>
                        </div>
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold">
                          {quiz.duration_minutes} mins
                        </span>
                      </div>
                      <p className="text-gray-700 mb-4">{quiz.description}</p>
                      <div className="flex justify-between items-center">
                        <div className="text-sm text-gray-600">
                          Ends: {new Date(quiz.end_time).toLocaleDateString()}
                        </div>
                        <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                          Start Quiz
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Attendance Tab */}
          {activeTab === 'attendance' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">📍 Attendance Records</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm mb-2">Overall Attendance</p>
                  <div className="flex items-center justify-between">
                    <p className="text-4xl font-bold text-green-600">
                      {attendance?.attendance_percentage.toFixed(1)}%
                    </p>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">
                        {attendance?.classes_attended}/{attendance?.total_classes}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm mb-2">This Month</p>
                  <p className="text-4xl font-bold text-blue-600">
                    {attendance?.month === new Date().getMonth() + 1
                      ? attendance.classes_attended
                      : 0}{' '}
                    classes
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm mb-2">Status</p>
                  <p
                    className={`text-xl font-bold ${
                      attendance?.attendance_percentage >= 75
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    {attendance?.attendance_percentage >= 75
                      ? '✅ Good'
                      : '⚠️ Low'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Marks Tab */}
          {activeTab === 'marks' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">📈 Consolidated Marks</h2>
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-100 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Assessment
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Marks Obtained
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Max Marks
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Percentage
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {assignments
                      .filter(a => a.marks_obtained !== null)
                      .map(a => (
                        <tr key={a.id} className="border-b hover:bg-gray-50">
                          <td className="px-6 py-3 text-sm text-gray-700">
                            {a.title}
                          </td>
                          <td className="px-6 py-3 text-sm text-gray-600">
                            Assignment
                          </td>
                          <td className="px-6 py-3 text-sm font-semibold text-gray-900">
                            {a.marks_obtained}
                          </td>
                          <td className="px-6 py-3 text-sm text-gray-600">
                            {a.max_marks}
                          </td>
                          <td className="px-6 py-3 text-sm">
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                              {(
                                (a.marks_obtained / a.max_marks) *
                                100
                              ).toFixed(1)}
                              %
                            </span>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tasks/Todos Tab */}
          {activeTab === 'todos' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">✓ My Tasks & To-Do List</h2>

              {/* AI Assistant */}
              <button
                onClick={() => setShowAiAssistant(!showAiAssistant)}
                className="mb-6 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition flex items-center gap-2"
              >
                🤖 {showAiAssistant ? 'Hide' : 'Open'} AI Assistant
              </button>

              {showAiAssistant && (
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow p-6 mb-6 border-l-4 border-purple-600">
                  <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                    🤖 AI Study Assistant
                  </h3>
                  <div className="bg-white rounded p-4 mb-4 h-48 overflow-y-auto">
                    <p className="text-sm text-gray-700 mb-3">
                      💡 <strong>Personalized Reminders for You:</strong>
                    </p>
                    <ul className="text-sm text-gray-600 space-y-2">
                      <li>
                        ✅ You have{' '}
                        {assignments.filter(a => a.status === 'pending').length}{' '}
                        pending assignments
                      </li>
                      <li>
                        🧪 {quizzes.filter(q => new Date(q.end_time) > new Date()).length}{' '}
                        active quizzes to complete
                      </li>
                      <li>
                        📚 {'Don\'t forget to review ' + yearName + ' notes'}
                      </li>
                      <li>
                        🎯 Your attendance is{' '}
                        {attendance?.attendance_percentage.toFixed(1)}% - Keep it
                        above 75%!
                      </li>
                      <li>📖 New study materials uploaded for your subjects</li>
                    </ul>
                  </div>
                  <input
                    type="text"
                    placeholder="Ask me anything about your studies..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-600"
                  />
                </div>
              )}

              {/* Add New Todo */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-lg font-bold mb-4">Add New Task</h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newTodo}
                    onChange={e => setNewTodo(e.target.value)}
                    onKeyPress={e =>
                      e.key === 'Enter' && handleAddTodo()
                    }
                    placeholder="Enter your task..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-600"
                  />
                  <button
                    onClick={handleAddTodo}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* Todos List */}
              <div className="bg-white rounded-lg shadow">
                {todos.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    No tasks. Great! You're all caught up! 🎉
                  </p>
                ) : (
                  <div className="divide-y">
                    {todos.map(todo => (
                      <div
                        key={todo.id}
                        className="p-4 flex items-center gap-3 hover:bg-gray-50"
                      >
                        <input
                          type="checkbox"
                          checked={todo.completed}
                          onChange={() => handleToggleTodo(todo.id)}
                          className="w-5 h-5 text-blue-600 rounded cursor-pointer"
                        />
                        <span
                          className={`flex-1 ${
                            todo.completed
                              ? 'line-through text-gray-400'
                              : 'text-gray-700'
                          }`}
                        >
                          {todo.title}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(
                            todo.created_at
                          ).toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
