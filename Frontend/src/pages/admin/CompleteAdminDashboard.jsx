import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function AdminDashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [students, setStudents] = useState([])
  const [selectedStudent, setSelectedStudent] = useState(null)
  const [assignments, setAssignments] = useState([])
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [showNewAssignment, setShowNewAssignment] = useState(false)
  const [showNewQuiz, setShowNewQuiz] = useState(false)
  const [showAttendance, setShowAttendance] = useState(false)
  const [showUploadContent, setShowUploadContent] = useState(false)

  // Form states
  const [newAssignment, setNewAssignment] = useState({
    title: '',
    description: '',
    subject_name: '',
    due_date: '',
    max_marks: 10,
  })

  const [newQuiz, setNewQuiz] = useState({
    title: '',
    description: '',
    subject_name: '',
    duration_minutes: 30,
    max_marks: 10,
  })

  const [attendance, setAttendance] = useState({
    date: new Date().toISOString().split('T')[0],
    students: [],
  })

  const [newContent, setNewContent] = useState({
    subject_name: '',
    content_type: '',
    title: '',
    year: 1,
    file_url: '',
  })

  // Fetch admin data
  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          navigate('/login')
          return
        }

        // Get analytics
        const analyticsRes = await api.get('/admin/analytics')
        setStats(analyticsRes.data)

        // Get all students
        const studentsRes = await api.get('/admin/students')
        setStudents(studentsRes.data || [])

        // Get assignments
        const assignmentsRes = await api.get('/admin/assignments')
        setAssignments(assignmentsRes.data || [])

        // Get quizzes
        const quizzesRes = await api.get('/admin/quizzes')
        setQuizzes(quizzesRes.data || [])

        setLoading(false)
      } catch (error) {
        console.error('Error fetching admin data:', error)
        setLoading(false)
      }
    }

    fetchAdminData()
  }, [navigate])

  const handleCreateAssignment = async () => {
    try {
      const response = await api.post('/admin/assignments', newAssignment)
      setAssignments([...assignments, response.data])
      setNewAssignment({
        title: '',
        description: '',
        subject_name: '',
        due_date: '',
        max_marks: 10,
      })
      setShowNewAssignment(false)
    } catch (error) {
      console.error('Error creating assignment:', error)
    }
  }

  const handleCreateQuiz = async () => {
    try {
      const response = await api.post('/admin/quizzes', newQuiz)
      setQuizzes([...quizzes, response.data])
      setNewQuiz({
        title: '',
        description: '',
        subject_name: '',
        duration_minutes: 30,
        max_marks: 10,
      })
      setShowNewQuiz(false)
    } catch (error) {
      console.error('Error creating quiz:', error)
    }
  }

  const handleUploadContent = async () => {
    try {
      const response = await api.post('/admin/content', newContent)
      setNewContent({
        subject_name: '',
        content_type: '',
        title: '',
        year: 1,
        file_url: '',
      })
      setShowUploadContent(false)
      // Show success message
      alert('Content uploaded successfully!')
    } catch (error) {
      console.error('Error uploading content:', error)
    }
  }

  const handleMarkAttendance = async () => {
    try {
      for (const student of attendance.students.filter(s => s.present)) {
        await api.post('/admin/attendance', {
          student_id: student.id,
          date: attendance.date,
          present: true,
        })
      }
      setAttendance({
        date: new Date().toISOString().split('T')[0],
        students: [],
      })
      setShowAttendance(false)
      alert('Attendance marked successfully!')
    } catch (error) {
      console.error('Error marking attendance:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading admin dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Admin Dashboard 👨‍💼
            </h1>
            <p className="text-gray-600 mt-1">Manage students, content, and assessments</p>
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

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Students</p>
                <p className="text-3xl font-bold text-blue-600">{students.length}</p>
              </div>
              <div className="text-4xl">👥</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Assignments</p>
                <p className="text-3xl font-bold text-orange-600">
                  {assignments.length}
                </p>
              </div>
              <div className="text-4xl">📝</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Quizzes</p>
                <p className="text-3xl font-bold text-purple-600">{quizzes.length}</p>
              </div>
              <div className="text-4xl">🧪</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Avg Class Strength</p>
                <p className="text-3xl font-bold text-green-600">
                  {stats?.average_attendance || 0}
                </p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="flex flex-wrap gap-2 p-4 border-b">
            {[
              { id: 'overview', label: '📊 Overview', icon: '📊' },
              { id: 'students', label: '👥 Students', icon: '👥' },
              { id: 'assignments', label: '📝 Assignments', icon: '📝' },
              { id: 'quizzes', label: '🧪 Quizzes', icon: '🧪' },
              { id: 'attendance', label: '📍 Attendance', icon: '📍' },
              { id: 'content', label: '📚 Upload Content', icon: '📚' },
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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Activities */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">📈 Quick Actions</h2>
                <div className="space-y-3">
                  <button
                    onClick={() => setShowNewAssignment(true)}
                    className="w-full p-4 text-left bg-orange-50 border border-orange-200 hover:bg-orange-100 rounded-lg transition"
                  >
                    <div className="font-semibold text-orange-900">
                      ➕ Create Assignment
                    </div>
                    <div className="text-sm text-orange-700">
                      Set new assignment for students
                    </div>
                  </button>

                  <button
                    onClick={() => setShowNewQuiz(true)}
                    className="w-full p-4 text-left bg-purple-50 border border-purple-200 hover:bg-purple-100 rounded-lg transition"
                  >
                    <div className="font-semibold text-purple-900">
                      ➕ Create Quiz
                    </div>
                    <div className="text-sm text-purple-700">
                      Create new quiz for assessment
                    </div>
                  </button>

                  <button
                    onClick={() => setShowAttendance(true)}
                    className="w-full p-4 text-left bg-green-50 border border-green-200 hover:bg-green-100 rounded-lg transition"
                  >
                    <div className="font-semibold text-green-900">
                      ✅ Mark Attendance
                    </div>
                    <div className="text-sm text-green-700">
                      Record attendance for today
                    </div>
                  </button>

                  <button
                    onClick={() => setShowUploadContent(true)}
                    className="w-full p-4 text-left bg-blue-50 border border-blue-200 hover:bg-blue-100 rounded-lg transition"
                  >
                    <div className="font-semibold text-blue-900">
                      📤 Upload Content
                    </div>
                    <div className="text-sm text-blue-700">
                      Upload notes, PPT, textbooks
                    </div>
                  </button>
                </div>
              </div>

              {/* AI Assistant for Admin */}
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg shadow p-6 border-l-4 border-indigo-600">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  🤖 Admin AI Assistant
                </h2>
                <div className="bg-white rounded p-4 mb-4 h-48 overflow-y-auto">
                  <p className="text-sm text-gray-700 font-semibold mb-3">
                    📊 Insights & Suggestions:
                  </p>
                  <ul className="text-sm text-gray-600 space-y-2">
                    <li>
                      ⚠️ {students.filter(s => s.attendance < 75).length} students
                      have low attendance
                    </li>
                    <li>
                      📝 {assignments.filter(a => a.status === 'pending').length}{' '}
                      assignments pending submission
                    </li>
                    <li>
                      🧪 Create more quizzes to improve assessment coverage
                    </li>
                    <li>
                      📚 Update {Math.random() > 0.5 ? '2nd Year' : '3rd Year'}{' '}
                      syllabus materials
                    </li>
                    <li>💡 Consider uploading practice papers for exams</li>
                  </ul>
                </div>
                <input
                  type="text"
                  placeholder="Ask for student insights, suggestions..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-600"
                />
              </div>
            </div>
          )}

          {/* Students Tab */}
          {activeTab === 'students' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">👥 Student List & Progress</h2>

              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-100 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Batch
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Department
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Attendance
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        GPA
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map(student => (
                      <tr key={student.id} className="border-b hover:bg-gray-50">
                        <td className="px-6 py-3 text-sm text-gray-700">
                          {student.name}
                        </td>
                        <td className="px-6 py-3 text-sm text-gray-600">
                          {student.batch_year}
                        </td>
                        <td className="px-6 py-3 text-sm text-gray-600">
                          {student.department}
                        </td>
                        <td className="px-6 py-3 text-sm">
                          <span
                            className={`px-3 py-1 rounded-full text-sm font-semibold ${
                              student.attendance_percentage >= 75
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {student.attendance_percentage?.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-3 text-sm font-semibold">
                          {student.gpa?.toFixed(2)}
                        </td>
                        <td className="px-6 py-3 text-sm">
                          <button
                            onClick={() => setSelectedStudent(student)}
                            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-xs"
                          >
                            View Progress
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Student Progress Modal */}
              {selectedStudent && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                  <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-96 overflow-y-auto">
                    <div className="p-6 border-b flex justify-between items-center">
                      <h3 className="text-xl font-bold">
                        {selectedStudent.name}'s Progress
                      </h3>
                      <button
                        onClick={() => setSelectedStudent(null)}
                        className="text-gray-500 hover:text-gray-700 text-2xl"
                      >
                        ×
                      </button>
                    </div>
                    <div className="p-6 space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-blue-50 p-4 rounded">
                          <p className="text-sm text-gray-600">GPA</p>
                          <p className="text-2xl font-bold text-blue-600">
                            {selectedStudent.gpa?.toFixed(2)}
                          </p>
                        </div>
                        <div className="bg-green-50 p-4 rounded">
                          <p className="text-sm text-gray-600">Attendance</p>
                          <p className="text-2xl font-bold text-green-600">
                            {selectedStudent.attendance_percentage?.toFixed(1)}%
                          </p>
                        </div>
                        <div className="bg-orange-50 p-4 rounded">
                          <p className="text-sm text-gray-600">Assignments</p>
                          <p className="text-2xl font-bold text-orange-600">
                            {selectedStudent.assignments_completed || 0}
                          </p>
                        </div>
                        <div className="bg-purple-50 p-4 rounded">
                          <p className="text-sm text-gray-600">Quizzes</p>
                          <p className="text-2xl font-bold text-purple-600">
                            {selectedStudent.quizzes_taken || 0}
                          </p>
                        </div>
                      </div>
                      <div className="mt-6">
                        <h4 className="font-bold mb-3">Suggestions</h4>
                        <ul className="text-sm text-gray-600 space-y-2">
                          <li>✓ Good GPA - Maintain this performance</li>
                          {selectedStudent.attendance_percentage < 75 && (
                            <li>
                              ⚠️ Improve attendance - Currently below 75%
                            </li>
                          )}
                          <li>
                            📝 Encourage more assignment submissions
                          </li>
                          <li>
                            🧪 Motivation needed for more quiz attempts
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Assignments Tab */}
          {activeTab === 'assignments' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">📝 Manage Assignments</h2>
                <button
                  onClick={() => setShowNewAssignment(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  + New Assignment
                </button>
              </div>

              {showNewAssignment && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                  <h3 className="text-lg font-bold mb-4">Create New Assignment</h3>
                  <div className="space-y-4">
                    <input
                      type="text"
                      placeholder="Title"
                      value={newAssignment.title}
                      onChange={e =>
                        setNewAssignment({
                          ...newAssignment,
                          title: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                    <input
                      type="text"
                      placeholder="Subject Name"
                      value={newAssignment.subject_name}
                      onChange={e =>
                        setNewAssignment({
                          ...newAssignment,
                          subject_name: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                    <textarea
                      placeholder="Description"
                      value={newAssignment.description}
                      onChange={e =>
                        setNewAssignment({
                          ...newAssignment,
                          description: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      rows="3"
                    />
                    <input
                      type="date"
                      value={newAssignment.due_date}
                      onChange={e =>
                        setNewAssignment({
                          ...newAssignment,
                          due_date: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                    <input
                      type="number"
                      placeholder="Max Marks"
                      value={newAssignment.max_marks}
                      onChange={e =>
                        setNewAssignment({
                          ...newAssignment,
                          max_marks: parseInt(e.target.value),
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={handleCreateAssignment}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        Create
                      </button>
                      <button
                        onClick={() => setShowNewAssignment(false)}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {assignments.map(assignment => (
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
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                        {assignment.max_marks} Marks
                      </span>
                    </div>
                    <p className="text-gray-700 mb-4">{assignment.description}</p>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">
                        Due: {new Date(assignment.due_date).toLocaleDateString()}
                      </span>
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                        Edit
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quizzes Tab */}
          {activeTab === 'quizzes' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">🧪 Manage Quizzes</h2>
                <button
                  onClick={() => setShowNewQuiz(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  + New Quiz
                </button>
              </div>

              {showNewQuiz && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                  <h3 className="text-lg font-bold mb-4">Create New Quiz</h3>
                  <div className="space-y-4">
                    <input
                      type="text"
                      placeholder="Title"
                      value={newQuiz.title}
                      onChange={e =>
                        setNewQuiz({ ...newQuiz, title: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                    <input
                      type="text"
                      placeholder="Subject Name"
                      value={newQuiz.subject_name}
                      onChange={e =>
                        setNewQuiz({
                          ...newQuiz,
                          subject_name: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                    <textarea
                      placeholder="Description"
                      value={newQuiz.description}
                      onChange={e =>
                        setNewQuiz({ ...newQuiz, description: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      rows="3"
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <input
                        type="number"
                        placeholder="Duration (minutes)"
                        value={newQuiz.duration_minutes}
                        onChange={e =>
                          setNewQuiz({
                            ...newQuiz,
                            duration_minutes: parseInt(e.target.value),
                          })
                        }
                        className="px-4 py-2 border border-gray-300 rounded-lg"
                      />
                      <input
                        type="number"
                        placeholder="Max Marks"
                        value={newQuiz.max_marks}
                        onChange={e =>
                          setNewQuiz({
                            ...newQuiz,
                            max_marks: parseInt(e.target.value),
                          })
                        }
                        className="px-4 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handleCreateQuiz}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        Create
                      </button>
                      <button
                        onClick={() => setShowNewQuiz(false)}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {quizzes.map(quiz => (
                  <div
                    key={quiz.id}
                    className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-lg font-bold">{quiz.title}</h3>
                        <p className="text-sm text-gray-600">{quiz.subject_name}</p>
                      </div>
                      <div className="flex gap-2">
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold">
                          {quiz.duration_minutes} mins
                        </span>
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                          {quiz.max_marks} Marks
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-700 mb-4">{quiz.description}</p>
                    <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm">
                      Edit Questions
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Attendance Tab */}
          {activeTab === 'attendance' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">📍 Mark Attendance</h2>
                <button
                  onClick={() => setShowAttendance(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  + Mark Today's Attendance
                </button>
              </div>

              {showAttendance && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                  <h3 className="text-lg font-bold mb-4">Mark Attendance</h3>
                  <div className="mb-4">
                    <label className="block text-sm font-semibold mb-2">
                      Date
                    </label>
                    <input
                      type="date"
                      value={attendance.date}
                      onChange={e =>
                        setAttendance({ ...attendance, date: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {students.map(student => (
                      <label
                        key={student.id}
                        className="flex items-center p-3 bg-gray-50 hover:bg-gray-100 rounded cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          onChange={e => {
                            const newStudents = attendance.students.includes(
                              student.id
                            )
                              ? attendance.students.filter(id => id !== student.id)
                              : [...attendance.students, student.id]

                            setAttendance({
                              ...attendance,
                              students: newStudents,
                            })
                          }}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <span className="ml-3 text-sm font-medium">
                          {student.name}
                        </span>
                      </label>
                    ))}
                  </div>

                  <div className="flex gap-2 mt-6">
                    <button
                      onClick={handleMarkAttendance}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      Save Attendance
                    </button>
                    <button
                      onClick={() => setShowAttendance(false)}
                      className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Upload Content Tab */}
          {activeTab === 'content' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">📚 Upload Study Materials</h2>

              {showUploadContent && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                  <h3 className="text-lg font-bold mb-4">Upload Content</h3>
                  <div className="space-y-4">
                    <select
                      value={newContent.year}
                      onChange={e =>
                        setNewContent({
                          ...newContent,
                          year: parseInt(e.target.value),
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value={1}>1st Year</option>
                      <option value={2}>2nd Year</option>
                      <option value={3}>3rd Year</option>
                      <option value={4}>4th Year</option>
                    </select>

                    <input
                      type="text"
                      placeholder="Subject Name"
                      value={newContent.subject_name}
                      onChange={e =>
                        setNewContent({
                          ...newContent,
                          subject_name: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />

                    <select
                      value={newContent.content_type}
                      onChange={e =>
                        setNewContent({
                          ...newContent,
                          content_type: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="">Select Type</option>
                      <option value="notes">Notes</option>
                      <option value="ppt">PowerPoint</option>
                      <option value="textbook">Textbook</option>
                      <option value="pyq">Previous Year Questions</option>
                      <option value="demo_test">Demo Test</option>
                      <option value="solutions">Solutions</option>
                    </select>

                    <input
                      type="text"
                      placeholder="Title"
                      value={newContent.title}
                      onChange={e =>
                        setNewContent({
                          ...newContent,
                          title: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />

                    <input
                      type="url"
                      placeholder="File URL or Drive Link"
                      value={newContent.file_url}
                      onChange={e =>
                        setNewContent({
                          ...newContent,
                          file_url: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />

                    <div className="flex gap-2">
                      <button
                        onClick={handleUploadContent}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        Upload
                      </button>
                      <button
                        onClick={() => setShowUploadContent(false)}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {!showUploadContent && (
                <button
                  onClick={() => setShowUploadContent(true)}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 mb-6"
                >
                  + Upload New Content
                </button>
              )}

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold mb-4">Upload Instructions</h3>
                <ol className="text-sm text-gray-600 space-y-2 list-decimal list-inside">
                  <li>Select the academic year</li>
                  <li>Enter subject name</li>
                  <li>Choose content type (notes, PPT, etc.)</li>
                  <li>
                    Provide a file URL (Google Drive, Dropbox, etc.)
                  </li>
                  <li>Content will automatically appear in student interface</li>
                  <li>
                    All students of that year will see updated content instantly
                  </li>
                </ol>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
