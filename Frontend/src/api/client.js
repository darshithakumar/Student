import axios from 'axios'

const API_BASE_URL = 'http://localhost:8001/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data) => api.post('/auth/register/student', data),
  login: (email, password) => api.post('/auth/login', { email, password }),
  validateToken: (token) => api.post('/auth/validate-token', { token }),
}

export const studentAPI = {
  getDashboard: () => api.get('/student/dashboard'),
  getAssignments: () => api.get('/student/assignments'),
  submitAssignment: (assignmentId, data) => api.post(`/student/assignments/${assignmentId}/submit`, data),
  getQuizzes: () => api.get('/student/quizzes/my-quizzes'),
  startQuiz: (quizId) => api.post(`/quizzes/${quizId}/start`),
  submitQuiz: (quizId, data) => api.post(`/quizzes/${quizId}/submit`, data),
  getAttendance: () => api.get('/student/attendance'),
  getMarks: () => api.get('/student/marks'),
  getNotifications: (unreadOnly = false) => api.get(`/student/notifications?unread_only=${unreadOnly}`),
  getTodos: () => api.get('/student/todos'),
  createTodo: (data) => api.post('/student/todos', data),
  updateTodo: (todoId, data) => api.put(`/student/todos/${todoId}`, data),
}

export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getStudents: (params) => api.get('/admin/students', { params }),
  getStudentDetails: (studentId) => api.get(`/admin/students/${studentId}`),
  markAttendance: (data) => api.post('/attendance/mark', data),
  markAttendanceBulk: (data) => api.post('/admin/attendance/bulk-mark', data),
  updateMarks: (data) => api.post('/admin/marks/update', data),
  updateMarksBulk: (data) => api.post('/admin/marks/bulk-update', data),
  getPendingSubmissions: () => api.get('/admin/assignments/pending'),
  gradeAssignment: (assignmentId, data) => api.post(`/admin/assignments/${assignmentId}/grade`, data),
  getAdminLogs: (params) => api.get('/admin/logs', { params }),
  getAttendanceReport: (params) => api.get('/admin/analytics/attendance-report', { params }),
}

export const contentAPI = {
  upload: (data) => api.post('/content/upload', data),
  update: (contentId, data) => api.put(`/content/${contentId}`, data),
  delete: (contentId) => api.delete(`/content/${contentId}`),
}

export const assignmentAPI = {
  create: (data) => api.post('/assignments/create', data),
  update: (assignmentId, data) => api.put(`/assignments/update/${assignmentId}`, data),
  getSubmissions: (assignmentId) => api.get(`/assignments/submissions/${assignmentId}`),
}

export const quizAPI = {
  create: (data) => api.post('/quizzes/create', data),
  addQuestion: (quizId, data) => api.post(`/quizzes/${quizId}/add-question`, data),
  getResponses: (quizId) => api.get(`/quizzes/${quizId}/responses`),
}

export default api
