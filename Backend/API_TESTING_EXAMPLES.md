# API Testing Guide - Example Requests

## 🧪 Testing Your College Academic Portal API

This guide provides ready-to-use API request examples for testing all endpoints.

---

## 📍 Base URL
```
http://localhost:8000
```

---

## 1️⃣ AUTHENTICATION APIs

### 1.1 Register a Student
```bash
curl -X POST "http://localhost:8000/api/auth/register/student" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@college.edu",
    "password": "SecurePassword123!",
    "name": "John Doe",
    "batch_year": 2020,
    "department": "CSE"
  }'

# Response:
{
  "message": "Student registered successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@college.edu",
  "name": "John Doe",
  "batch_year": 2020,
  "department": "CSE"
}
```

### 1.2 Register an Admin
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@college.edu",
    "password": "AdminPassword123!",
    "role": "admin",
    "name": "Admin User"
  }'

# Response:
{
  "message": "User registered successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "email": "admin@college.edu",
  "role": "admin"
}
```

### 1.3 Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@college.edu",
    "password": "SecurePassword123!"
  }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "student"
}

# Save token for next requests:
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 1.4 Validate Token
```bash
curl -X POST "http://localhost:8000/api/auth/validate-token" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'

# Response:
{
  "valid": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@college.edu",
  "role": "student"
}
```

---

## 2️⃣ STUDENT APIs

### 2.1 Get Student Dashboard (⭐ MAIN ENDPOINT)
```bash
curl -X GET "http://localhost:8000/api/student/dashboard" \
  -H "Authorization: Bearer $TOKEN"

# Response (Large JSON with all dashboard data):
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "batch_year": 2020,
  "current_year": 4,
  "department": "CSE",
  "academic_content": {
    "year": 4,
    "semester": 1,
    "notes": [
      {
        "id": "uuid",
        "subject_name": "Data Structures",
        "title": "Chapter 5: Hash Tables",
        "file_url": "https://...",
        "uploaded_at": "2026-02-07T10:00:00",
        "version": 1
      }
    ],
    "ppts": [...],
    "textbooks": [...],
    "pyqs": [...],
    "demo_tests": [...]
  },
  "assignments": [
    {
      "id": "uuid",
      "title": "Build a Hash Table",
      "subject": "Data Structures",
      "due_date": "2026-02-15T23:59:59",
      "max_marks": 10,
      "status": "pending"
    }
  ],
  "quizzes": [...],
  "progress": {
    "gpa": 3.8,
    "total_assignments_completed": 12,
    "total_quizzes_attempted": 15
  },
  "attendance": {
    "total_classes": 45,
    "classes_attended": 43,
    "attendance_percentage": 95.6
  },
  "consolidated_marks": {...},
  "notifications": [...],
  "todo_reminders": [...]
}
```

### 2.2 Get My Assignments
```bash
curl -X GET "http://localhost:8000/api/student/assignments" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "assignments": [
    {
      "id": "uuid",
      "assignment_id": "uuid",
      "status": "pending",
      "submission_date": null,
      "marks_obtained": null,
      "feedback": null
    }
  ],
  "total": 5
}
```

### 2.3 Submit an Assignment
```bash
curl -X POST "http://localhost:8000/api/student/assignments/{assignment_id}/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "submission_file_url": "https://files.example.com/submission123.pdf"
  }'

# Response:
{
  "message": "Assignment submitted successfully",
  "submission_date": "2026-02-10T15:30:00"
}
```

### 2.4 Get My Quizzes
```bash
curl -X GET "http://localhost:8000/api/student/quizzes/my-quizzes" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "quizzes": [
    {
      "id": "uuid",
      "quiz_id": "uuid",
      "status": "in_progress",
      "marks_obtained": null,
      "start_time": "2026-02-07T14:00:00",
      "end_time": "2026-02-07T14:30:00"
    }
  ],
  "total": 3
}
```

### 2.5 Start a Quiz
```bash
curl -X POST "http://localhost:8000/api/quizzes/{quiz_id}/start" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "message": "Quiz started",
  "quiz_id": "uuid",
  "questions": [
    {
      "id": "uuid",
      "question": "What is a hash table?",
      "type": "mcq",
      "options": ["A", "B", "C", "D"],
      "marks": 1,
      "order": 1
    }
  ]
}
```

### 2.6 Submit Quiz Answers
```bash
curl -X POST "http://localhost:8000/api/quizzes/{quiz_id}/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {
        "question_id": "uuid",
        "answer": "A"
      },
      {
        "question_id": "uuid",
        "answer": "B"
      }
    ]
  }'

# Response:
{
  "message": "Quiz submitted successfully",
  "marks_obtained": 8
}
```

### 2.7 Get My Attendance
```bash
curl -X GET "http://localhost:8000/api/student/attendance" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "month": 2,
  "year": 2026,
  "total_classes": 45,
  "classes_attended": 43,
  "attendance_percentage": 95.6
}
```

### 2.8 Get My Marks
```bash
curl -X GET "http://localhost:8000/api/student/marks" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "student_id": "uuid",
  "overall_percentage": 87.5,
  "marks_by_subject": [
    {
      "id": "uuid",
      "subject_name": "Data Structures",
      "exam_type": "midterm",
      "marks_obtained": 85,
      "max_marks": 100,
      "percentage": 85.0,
      "grade": "A"
    }
  ],
  "total_records": 5
}
```

### 2.9 Get My Notifications
```bash
curl -X GET "http://localhost:8000/api/student/notifications?unread_only=true" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "notifications": [
    {
      "id": "uuid",
      "title": "New Assignment Posted",
      "message": "Assignment 'Build Hash Table' has been posted",
      "type": "assignment",
      "is_read": false,
      "created_at": "2026-02-07T10:00:00"
    }
  ],
  "total": 3
}
```

### 2.10 Mark Notification as Read
```bash
curl -X PUT "http://localhost:8000/api/student/notifications/{notification_id}/read" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "message": "Notification marked as read"
}
```

### 2.11 Get My TODOs
```bash
curl -X GET "http://localhost:8000/api/student/todos" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "todos": [
    {
      "id": "uuid",
      "task": "Complete Data Structures Assignment",
      "priority": "high",
      "due_date": "2026-02-15T23:59:59",
      "category": "assignment",
      "completed": false
    }
  ],
  "total": 5
}
```

### 2.12 Create a TODO
```bash
curl -X POST "http://localhost:8000/api/student/todos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_title": "Study for Final Exam",
    "description": "Chapter 1-10",
    "due_date": "2026-02-28T23:59:59",
    "priority": "high",
    "category": "study"
  }'

# Response:
{
  "id": "uuid",
  "task": "Study for Final Exam",
  "message": "TODO reminder created successfully"
}
```

### 2.13 Update a TODO
```bash
curl -X PUT "http://localhost:8000/api/student/todos/{todo_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_completed": true
  }'

# Response:
{
  "message": "TODO updated successfully",
  "todo_id": "uuid"
}
```

---

## 3️⃣ ADMIN APIs

### 3.1 Admin Dashboard
```bash
curl -X GET "http://localhost:8000/api/admin/dashboard" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "total_students": 150,
  "total_assignments": 25,
  "total_quizzes": 10,
  "pending_submissions": 8,
  "average_attendance": 92.3
}
```

### 3.2 Get All Students
```bash
curl -X GET "http://localhost:8000/api/admin/students?department=CSE&batch_year=2020" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "students": [
    {
      "user_id": "uuid",
      "name": "John Doe",
      "batch_year": 2020,
      "department": "CSE",
      "current_year": 4
    }
  ],
  "total": 30
}
```

### 3.3 Get Student Details
```bash
curl -X GET "http://localhost:8000/api/admin/students/{student_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "student": {
    "user_id": "uuid",
    "name": "John Doe",
    "batch_year": 2020,
    "department": "CSE",
    "current_year": 4
  },
  "progress": {
    "gpa": 3.8,
    "total_assignments_completed": 12
  },
  "attendance": {
    "attendance_percentage": 95.6
  },
  "marks": {...}
}
```

### 3.4 Mark Attendance (Single)
```bash
curl -X POST "http://localhost:8000/api/attendance/mark" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "uuid",
    "date": "2026-02-07",
    "present": true
  }'

# Response:
{
  "message": "Attendance marked successfully"
}
```

### 3.5 Mark Attendance (Bulk)
```bash
curl -X POST "http://localhost:8000/api/admin/attendance/bulk-mark" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-07",
    "attendance_records": [
      {
        "student_id": "uuid1",
        "present": true
      },
      {
        "student_id": "uuid2",
        "present": false
      },
      {
        "student_id": "uuid3",
        "present": true
      }
    ]
  }'

# Response:
{
  "message": "Attendance marked for 3 students"
}
```

### 3.6 Update Student Marks
```bash
curl -X POST "http://localhost:8000/api/admin/marks/update" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "uuid",
    "subject_name": "Data Structures",
    "exam_type": "midterm",
    "marks_obtained": 85,
    "max_marks": 100
  }'

# Response:
{
  "message": "Marks updated successfully",
  "grade": "A",
  "percentage": 85.0
}
```

### 3.7 Bulk Update Marks
```bash
curl -X POST "http://localhost:8000/api/admin/marks/bulk-update" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "marks_records": [
      {
        "student_id": "uuid1",
        "subject_name": "Data Structures",
        "exam_type": "midterm",
        "marks_obtained": 85,
        "max_marks": 100
      },
      {
        "student_id": "uuid2",
        "subject_name": "Data Structures",
        "exam_type": "midterm",
        "marks_obtained": 90,
        "max_marks": 100
      }
    ]
  }'

# Response:
{
  "message": "Marks updated for 2 records",
  "total_records": 2
}
```

### 3.8 Get Pending Submissions
```bash
curl -X GET "http://localhost:8000/api/admin/assignments/pending" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "pending_submissions": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "assignment_id": "uuid",
      "submission_date": "2026-02-10T15:30:00",
      "status": "submitted"
    }
  ],
  "total": 8
}
```

### 3.9 Grade an Assignment
```bash
curl -X POST "http://localhost:8000/api/admin/assignments/{assignment_id}/grade" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "uuid",
    "marks": 8.5,
    "feedback": "Great implementation! Well structured code."
  }'

# Response:
{
  "message": "Assignment graded successfully",
  "marks": 8.5
}
```

### 3.10 Get Admin Logs
```bash
curl -X GET "http://localhost:8000/api/admin/logs?limit=50" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "logs": [
    {
      "id": "uuid",
      "admin_id": "uuid",
      "action": "create",
      "entity_type": "content",
      "timestamp": "2026-02-07T10:00:00",
      "changes": {
        "subject": "Data Structures",
        "type": "notes"
      }
    }
  ],
  "total": 45
}
```

### 3.11 Get Attendance Report
```bash
curl -X GET "http://localhost:8000/api/admin/analytics/attendance-report?department=CSE" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "attendance_report": [
    {
      "student_id": "uuid",
      "name": "John Doe",
      "attendance_percentage": 95.6
    }
  ],
  "total_students": 30
}
```

---

## 4️⃣ CONTENT MANAGEMENT APIs

### 4.1 Upload Content
```bash
curl -X POST "http://localhost:8000/api/content/upload" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "academic_year_id": "uuid",
    "subject_name": "Data Structures",
    "content_type": "notes",
    "title": "Chapter 5: Hash Tables",
    "description": "Comprehensive notes on hash tables",
    "file_url": "https://files.example.com/hash-tables.pdf"
  }'

# Response:
{
  "id": "uuid",
  "subject_name": "Data Structures",
  "content_type": "notes",
  "title": "Chapter 5: Hash Tables",
  "uploaded_at": "2026-02-07T10:00:00",
  "version": 1
}
```

### 4.2 Update Content
```bash
curl -X PUT "http://localhost:8000/api/content/{content_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_name": "Data Structures",
    "content_type": "notes",
    "title": "Chapter 5: Hash Tables (Updated)",
    "description": "Enhanced notes with more examples",
    "file_url": "https://files.example.com/hash-tables-v2.pdf"
  }'

# Response:
{
  "id": "uuid",
  "title": "Chapter 5: Hash Tables (Updated)",
  "version": 2,
  "uploaded_at": "2026-02-07T11:00:00"
}
```

### 4.3 Delete Content
```bash
curl -X DELETE "http://localhost:8000/api/content/{content_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "message": "Content deleted successfully"
}
```

---

## 5️⃣ ASSIGNMENT MANAGEMENT APIs

### 5.1 Create Assignment
```bash
curl -X POST "http://localhost:8000/api/assignments/create" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "academic_year_id": "uuid",
    "subject_name": "Data Structures",
    "title": "Build a Hash Table",
    "description": "Implement a hash table with collision handling",
    "instructions": "Use separate chaining...",
    "file_url": "https://...",
    "due_date": "2026-02-15T23:59:59",
    "max_marks": 10
  }'

# Response:
{
  "message": "Assignment created successfully",
  "assignment_id": "uuid",
  "students_notified": 50
}
```

### 5.2 Update Assignment
```bash
curl -X PUT "http://localhost:8000/api/assignments/update/{assignment_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "due_date": "2026-02-20T23:59:59"
  }'

# Response:
{
  "message": "Assignment updated successfully"
}
```

### 5.3 Get Assignment Submissions
```bash
curl -X GET "http://localhost:8000/api/assignments/submissions/{assignment_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "submissions": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "status": "submitted",
      "submission_date": "2026-02-10T15:30:00",
      "marks_obtained": null
    }
  ],
  "total": 50,
  "submitted": 45,
  "graded": 32
}
```

---

## 6️⃣ QUIZ MANAGEMENT APIs

### 6.1 Create Quiz
```bash
curl -X POST "http://localhost:8000/api/quizzes/create" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "academic_year_id": "uuid",
    "subject_name": "Data Structures",
    "title": "Quiz 1: Hash Tables",
    "description": "Test your knowledge on hash tables",
    "max_marks": 10,
    "duration_minutes": 30,
    "start_time": "2026-02-15T14:00:00",
    "end_time": "2026-02-15T14:30:00"
  }'

# Response:
{
  "message": "Quiz created successfully",
  "quiz_id": "uuid",
  "students_notified": 50
}
```

### 6.2 Add Question to Quiz
```bash
curl -X POST "http://localhost:8000/api/quizzes/{quiz_id}/add-question" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is a hash table?",
    "question_type": "mcq",
    "options": ["Arrays", "Trees", "Maps", "Graphs"],
    "correct_answer": "Maps",
    "marks": 1,
    "order": 1
  }'

# Response:
{
  "message": "Question added successfully",
  "question_id": "uuid"
}
```

### 6.3 Get Quiz Responses
```bash
curl -X GET "http://localhost:8000/api/quizzes/{quiz_id}/responses" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
{
  "responses": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "status": "submitted",
      "marks_obtained": 8,
      "start_time": "2026-02-15T14:00:00",
      "end_time": "2026-02-15T14:28:00"
    }
  ],
  "total": 50,
  "submitted": 48,
  "graded": 48
}
```

---

## 🧪 Testing Tips

### Use Postman
1. Download Postman
2. Import endpoints as collection
3. Set environment variables: `TOKEN`, `ADMIN_TOKEN`
4. Run requests with a single click

### Use Python Requests
```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "email": "john.doe@college.edu",
        "password": "SecurePassword123!"
    }
)
token = response.json()["access_token"]

# Get dashboard
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    f"{BASE_URL}/api/student/dashboard",
    headers=headers
)
dashboard = response.json()
print(f"Current Year: {dashboard['current_year']}")
```

### Use JavaScript/Fetch
```javascript
const BASE_URL = "http://localhost:8000";

// Login
const loginResponse = await fetch(`${BASE_URL}/api/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "john.doe@college.edu",
    password: "SecurePassword123!"
  })
});
const { access_token } = await loginResponse.json();

// Get dashboard
const dashboardResponse = await fetch(
  `${BASE_URL}/api/student/dashboard`,
  {
    headers: { "Authorization": `Bearer ${access_token}` }
  }
);
const dashboard = await dashboardResponse.json();
console.log(`Current Year: ${dashboard.current_year}`);
```

---

## ✅ Success Indicators

- ✅ Status code 200 = Success
- ✅ Status code 201 = Created
- ✅ Status code 400 = Bad request
- ✅ Status code 401 = Unauthorized (missing token)
- ✅ Status code 403 = Forbidden (wrong role)
- ✅ Status code 404 = Not found
- ✅ Status code 500 = Server error

---

**Happy Testing! 🚀**
