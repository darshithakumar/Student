# System Architecture & Data Flow Diagrams

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vite + React)                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ StudentDashboard        AdministratorDashboard             │  │
│  │ - Auto-calculated year  - Student tracking                 │  │
│  │ - Year-specific content - Attendance management            │  │
│  │ - Assignments/Quizzes   - Content management               │  │
│  │ - Progress tracking     - Marks management                 │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                         │
│                    http://localhost:8000                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ CORS Middleware              JWT Authentication            │  │
│  │ - Frontend origin            - Token validation            │  │
│  │ - Content negotiation        - Role-based access control   │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────┐        ┌────────┐        ┌────────┐
    │ Auth   │        │Student │        │ Admin  │
    │Router  │        │ Router │        │ Router │
    └────────┘        └────────┘        └────────┘
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────────────────────────────────────────┐
   │ BUSINESS LOGIC LAYER (Services)             │
   │ ┌───────────────────────────────────────┐   │
   │ │ AcademicService  ← CORE AUTOMATION    │   │
   │ │ - Year calculation                    │   │
   │ │ - Content filtering                   │   │
   │ │ - Assignment distribution             │   │
   │ │ - Quiz distribution                   │   │
   │ │ - Progress tracking                   │   │
   │ │ - Attendance summaries                │   │
   │ │ - Notification creation               │   │
   │ └───────────────────────────────────────┘   │
   │ ┌───────────────────────────────────────┐   │
   │ │ AdminService, AnalyticsService, etc.  │   │
   │ └───────────────────────────────────────┘   │
   └─────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │Content  │  │ Assignment
   │Manager  │  │   Router │
   │Router   │  └─────────┘
   └─────────┘
        │       ┌──────────────┐
        │       │ Quiz Router  │
        │       └──────────────┘
        │
        ▼
   ┌───────────────────────────────────────────────────┐
   │ DATA ACCESS LAYER (SQLAlchemy ORM)                │
   │ Models: User, Student, Content, Assignment, etc.  │
   └───────────────────┬─────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   PostgreSQL DB       │
            │                       │
            │ ┌─────────────────┐   │
            │ │ users table     │   │
            │ │ students table  │   │
            │ │ academic_year   │   │
            │ │ content table   │   │
            │ │ assignments     │   │
            │ │ quizzes         │   │
            │ │ attendance      │   │
            │ │ marks           │   │
            │ │ notifications   │   │
            │ │ admin_logs      │   │
            │ └─────────────────┘   │
            └──────────────────────┘
```

---

## 🔄 Data Flow: Student Login & Dashboard Load

```
STUDENT LOGIN FLOW:
═════════════════════════════════════════════════════════════════

1️⃣ REGISTRATION (One-time)
   ┌──────────────────┐
   │ Student fills:   │
   │ - Email          │
   │ - Password       │
   │ - Name           │
   │ - Batch Year     │ ← KEY!
   │ - Department     │
   └──────────┬───────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ POST /api/auth/register/student   │
   └──────────┬───────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ Backend:                         │
   │ ✓ Hash password with bcrypt      │
   │ ✓ Create User record             │
   │ ✓ Create Student record          │
   │   (with batch_year = 2020)       │
   │ ✓ Save to PostgreSQL             │
   └──────────┬───────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ Response:                        │
   │ {                                │
   │   "user_id": "uuid",             │
   │   "email": "student@college.edu",│
   │   "batch_year": 2020             │
   │ }                                │
   └──────────────────────────────────┘

2️⃣ LOGIN
   ┌──────────────────┐
   │ Student enters:  │
   │ - Email          │
   │ - Password       │
   └──────────┬───────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ POST /api/auth/login             │
   └──────────┬───────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ Backend:                         │
   │ ✓ Query: Find user by email      │
   │ ✓ Verify password (bcrypt)       │
   │ ✓ Create JWT token               │
   │ ✓ Return token                   │
   └──────────┬───────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ Response:                        │
   │ {                                │
   │   "access_token": "ey...",       │
   │   "token_type": "bearer",        │
   │   "user_id": "uuid"              │
   │ }                                │
   └────────────┬────────────────────┘
                │ Save token to localStorage
                │
                ▼
   ┌──────────────────────────────────┐
   │ Frontend stores token &          │
   │ redirects to dashboard           │
   └──────────────────────────────────┘

3️⃣ DASHBOARD REQUEST (⭐ THE MAGIC HAPPENS HERE)
   ┌──────────────────┐
   │ User clicks:     │
   │ "Dashboard"      │
   └──────────┬───────┘
              │
              ▼
   ┌──────────────────────────────────────────┐
   │ GET /api/student/dashboard               │
   │ Header: Authorization: Bearer {token}    │
   └──────────┬───────────────────────────────┘
              │
              ▼
   ┌────────────────────────────────────────────┐
   │ Backend: verify_token (JWT validation)    │
   │ ✓ Parse JWT                               │
   │ ✓ Extract user_id = "abc123"              │
   │ ✓ Validate signature                      │
   └──────────┬─────────────────────────────────┘
              │
              ▼
   ┌────────────────────────────────────────────┐
   │ AcademicService.get_student_dashboard()    │
   │                                            │
   │ ⭐ CORE LOGIC:                             │
   │ 1. Query: SELECT * FROM students          │
   │    WHERE user_id = "abc123"               │
   │    Result: student.batch_year = 2020      │
   │                                            │
   │ 2. CALCULATE YEAR:                         │
   │    current_year = 2026 - 2020 + 1         │
   │    current_year = 7 → CAPPED AT 4         │
   │    ➜ Result: current_year = 4             │
   │                                            │
   │ 3. Query academic_content:                 │
   │    SELECT * FROM academic_content WHERE   │
   │    academic_year_id IN (                   │
   │      SELECT id FROM academic_years        │
   │      WHERE year = 4 AND semester = 1      │
   │      AND department = "CSE"               │
   │    )                                       │
   │    ➜ Result: Only 4th year notes/PPTs     │
   │                                            │
   │ 4. Query assignments:                      │
   │    SELECT * FROM assignments WHERE        │
   │    academic_year_id = (year 4 id)         │
   │    ➜ Result: Only 4th year assignments    │
   │                                            │
   │ 5. Query quizzes:                          │
   │    SELECT * FROM quizzes WHERE            │
   │    academic_year_id = (year 4 id)         │
   │    ➜ Result: Only 4th year quizzes        │
   │                                            │
   │ 6. Get attendance, progress, marks, etc.   │
   │                                            │
   │ 7. Aggregate all data                      │
   └──────────┬─────────────────────────────────┘
              │
              ▼
   ┌────────────────────────────────────────────────────────┐
   │ Response (COMPLETE DASHBOARD):                         │
   │ {                                                      │
   │   "student_id": "abc123",                              │
   │   "name": "John Doe",                                  │
   │   "batch_year": 2020,                                  │
   │   "current_year": 4,  ← AUTO-CALCULATED!              │
   │   "academic_content": {                                │
   │     "year": 4,                                         │
   │     "semester": 1,                                     │
   │     "notes": [                    ← 4TH YEAR ONLY      │
   │       {"id": "...", "title": "DSA Chapter 5", ...}     │
   │     ],                                                 │
   │     "ppts": [...],                ← 4TH YEAR ONLY      │
   │     "textbooks": [...],           ← 4TH YEAR ONLY      │
   │     "pyqs": [...],                ← 4TH YEAR ONLY      │
   │     "demo_tests": [...]           ← 4TH YEAR ONLY      │
   │   },                                                   │
   │   "assignments": [                                     │
   │     {                                                  │
   │       "title": "Build a Compiler",                     │
   │       "due_date": "2026-02-15",                        │
   │       "status": "pending"                              │
   │     }                             ← 4TH YEAR ONLY      │
   │   ],                                                   │
   │   "quizzes": [...],               ← 4TH YEAR ONLY      │
   │   "progress": {                                        │
   │     "gpa": 3.8,                                        │
   │     "assignments_completed": 12                        │
   │   },                                                   │
   │   "attendance": {                                      │
   │     "percentage": 95.6,                                │
   │     "classes_attended": 43/45                          │
   │   },                                                   │
   │   "consolidated_marks": {...},                         │
   │   "notifications": [...]                               │
   │ }                                                      │
   └────────────────────────────────────────────────────────┘
              │
              ▼
   ┌────────────────────────────────────────────────────────┐
   │ Frontend receives data                                 │
   │ ✓ Display: "Welcome, John! You're in Year 4"          │
   │ ✓ Display all 4th year materials automatically        │
   │ ✓ Display assignments, quizzes, attendance            │
   │ ✓ NO FILTERING, NO SEARCHING NEEDED!                  │
   └────────────────────────────────────────────────────────┘

⏰ TIME TRAVEL EXAMPLE:
═════════════════════════════════════════════════════════════════

SAME STUDENT, DIFFERENT YEARS:

Year 2020 (Now)
  Batch 2020 login → 2020 - 2020 + 1 = 1 → 1ST YEAR ✓
  Dashboard shows: 1st year notes, assignments, quizzes

Year 2021 (Next year)
  Batch 2020 login → 2021 - 2020 + 1 = 2 → 2ND YEAR ✓
  Dashboard shows: 2nd year notes, assignments, quizzes
  (Admin already uploaded 2nd year content)

Year 2022 (Next year)
  Batch 2020 login → 2022 - 2020 + 1 = 3 → 3RD YEAR ✓
  Dashboard shows: 3rd year notes, assignments, quizzes

Year 2023 (Next year)
  Batch 2020 login → 2023 - 2020 + 1 = 4 → 4TH YEAR ✓
  Dashboard shows: 4th year notes, assignments, quizzes

Year 2024 & beyond
  Batch 2020 login → 2024 - 2020 + 1 = 5 → CAPPED AT 4 → 4TH YEAR ✓
  (Student has graduated, sees 4th year content)

ALL AUTOMATIC! NO CODE CHANGES NEEDED!
```

---

## 📚 Academic Content Type Mapping

```
┌────────────────────────────────────────────────┐
│ content_type in academic_content table         │
├────────────────────────────────────────────────┤
│ "notes"       → Lecture notes/documents        │
│ "ppt"         → PowerPoint presentations       │
│ "textbook"    → Reference books/textbooks      │
│ "pyq"         → Previous Year Questions        │
│ "demo_test"   → Practice/Demo tests            │
└────────────────────────────────────────────────┘

Dashboard Organization:
┌──────────────────────────────────────┐
│ academic_content field:              │
├──────────────────────────────────────┤
│ {                                    │
│   "notes": [                         │
│     {content_type="notes"}           │
│   ],                                 │
│   "ppts": [                          │
│     {content_type="ppt"}             │
│   ],                                 │
│   "textbooks": [                     │
│     {content_type="textbook"}        │
│   ],                                 │
│   "pyqs": [                          │
│     {content_type="pyq"}             │
│   ],                                 │
│   "demo_tests": [                    │
│     {content_type="demo_test"}       │
│   ]                                  │
│ }                                    │
└──────────────────────────────────────┘
```

---

## 🔐 JWT Token Structure

```
JWT Token = Header.Payload.Signature

Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "user_id_uuid",          ← User's unique ID
  "email": "user@college.edu",    ← User's email
  "role": "student",              ← Role for auth
  "exp": 1707427200               ← Expiration time
}

Signature: HMAC(Header+Payload, SECRET_KEY)

Complete Token Example:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJ1c2VyLWlkIiwiZW1haWwiOiJ1c2VyQGNvbGxlZ2UuZWR1Iiw
icm9sZSI6InN0dWRlbnQifQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

---

## 📊 Database Relationships Diagram

```
User (1) ──────────── (1) Student
  │
  ├─────────────────────────── (1) StudentProgress
  │
  ├─────────────────────────── (N) StudentAssignment → Assignment
  │
  ├─────────────────────────── (N) StudentQuiz → Quiz
  │
  ├─────────────────────────── (N) Attendance
  │
  ├─────────────────────────── (N) StudentMarks
  │
  ├─────────────────────────── (N) Notification
  │
  ├─────────────────────────── (N) TodoReminder
  │
  └─────────────────────────── (N) AdminLog

AcademicYear (1) ─────────────────── (N) AcademicContent
     │
     ├─────────────── (N) Assignment
     │                      │
     │                      └─── (N) StudentAssignment
     │
     └─────────────── (N) Quiz
                            │
                            ├─── (N) QuizQuestion
                            │
                            └─── (N) StudentQuiz
```

---

## ⚙️ Request/Response Cycle

```
CLIENT REQUEST                  BACKEND PROCESSING          DATABASE
═════════════════════════════════════════════════════════════════════

GET /API/STUDENT/DASHBOARD
Header: Authorization: Bearer {token}
        ↓
        ├─ FastAPI receives request
        │
        ├─ CORS middleware checks origin
        │
        ├─ Route handler: @app.get("/dashboard")
        │
        ├─ Dependency: verify_token()
        │   ├─ Extract JWT from header
        │   ├─ Verify signature
        │   ├─ Extract user_id
        │
        ├─ Academic Service: get_student_dashboard()
        │   ├─ Query: users table → User object
        │   ├─ Query: students table → batch_year
        │   │
        │   ├─ CALCULATE: current_year = NOW - batch_year + 1
        │   │
        │   ├─ Query: academic_years WHERE year = current_year
        │   │   ↓ Get academic_year_id
        │   │
        │   ├─ Query: academic_content WHERE academic_year_id = ?
        │   │   ↓ Get notes, PPTs, textbooks, etc.
        │   │
        │   ├─ Query: assignments WHERE academic_year_id = ?
        │   │   ↓ Get year-specific assignments
        │   │
        │   ├─ Query: student_progress, attendance, marks
        │   │
        │   ├─ Organize all data
        │   └─ Return dictionary
        │
        ├─ Pydantic Schema validation
        │
        ├─ JSONify response
        │
        ↓
        Return 200 OK with JSON
```

---

## 🎯 Key Decision Points in Code

```
1️⃣ Student Registration
   └─ Store batch_year ✓ (Critical!)

2️⃣ Student Login
   └─ Generate JWT with user_id ✓

3️⃣ Dashboard Access
   └─ Verify JWT ✓
   └─ Extract user_id ✓
   └─ Query student.batch_year ✓
   └─ Calculate current_year ✓
   └─ Filter ALL content by current_year ✓

4️⃣ Admin Uploads Content
   └─ Associate with academic_year.year ✓
   └─ Next login will pick it up automatically ✓

5️⃣ Admin Creates Assignment
   └─ Associate with academic_year ✓
   └─ Auto-create StudentAssignment for all matching students ✓
   └─ Send notifications ✓
```

---

## 📈 Scalability Considerations

```
Per 1000 Students:
├─ User Queries: O(1) - Single lookup
├─ Student Queries: O(1) - Single lookup
├─ Content Queries: O(N) where N = materials for year
│   Indexed by: academic_year_id, content_type
├─ Assignment Queries: O(N) where N = assignments for year
│   Indexed by: academic_year_id
└─ Overall Dashboard Load: < 100ms with proper indexing

Caching Strategy:
├─ Cache academic_years (static, changes once/year)
├─ Cache academic_content (update only on admin action)
├─ Cache student progress (update on assignment/quiz)
└─ Live: attendance, notifications

Database Indexes (already added in models):
├─ students(batch_year, department)
├─ academic_content(academic_year_id, content_type)
├─ assignments(academic_year_id)
├─ attendance(student_id, date)
└─ student_progress(student_id)
```

---

**Diagram Created**: February 7, 2026  
**Last Updated**: February 7, 2026
