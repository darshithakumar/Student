# 🎓 College Academic Portal

A comprehensive web-based academic management system for colleges designed to streamline student and admin operations with real-time dashboards, assignment tracking, quizzes, attendance management, and performance analytics.
---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [Features](#features)
- [Test Credentials](#test-credentials)
- [API Endpoints](#api-endpoints)
- [Database](#database)
- [Project Architecture](#project-architecture)
- [Troubleshooting](#troubleshooting)

---

## 📖 Project Overview

The **College Academic Portal** is a full-stack web application built to help colleges manage their academic operations efficiently. It provides:

- **Student Dashboard** - View assignments, quizzes, grades, attendance, and study materials
- **Admin Dashboard** - Manage students, track performance, upload content, and monitor analytics
- **Automated Features** - Smart year calculation, auto-generated content based on academic level
- **Real-time Data** - Live attendance tracking, instant notifications, grade updates
- **Responsive Design** - Works seamlessly on desktop and mobile devices

### Key Highlights:
✅ JWT Authentication & Authorization  
✅ Role-based Access Control (Student/Admin)  
✅ SQLite Database with persistent storage  
✅ Real-time API Integration  
✅ Responsive UI with Tailwind CSS  
✅ RESTful API Architecture  

---

## 🛠️ Technology Stack

### **Frontend**
- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### **Backend**
- **FastAPI** - Web framework (Python)
- **SQLAlchemy** - ORM
- **SQLite** - Database (PostgreSQL compatible)
- **Python-Jose** - JWT tokens
- **Passlib** - Password hashing
- **Pydantic** - Data validation

### **Tools**
- **Node.js & npm** - Frontend dependencies
- **Python 3.11** - Backend runtime
- **Virtual Environment** - Python isolation

---

## ✨ Key Features

### 🎓 Student Interface
- ✅ Auto-loaded dashboard with year-specific content
- ✅ Assignment management and submission
- ✅ Quiz system with auto-grading
- ✅ Attendance tracking
- ✅ Consolidated marks viewing
- ✅ Notifications system
- ✅ TODO management

### 👨‍💼 Administrator Interface
- ✅ Student tracking and filtering
- ✅ Batch-based assignment auto-distribution
- ✅ Bulk attendance marking
- ✅ Bulk marks management
- ✅ Content management (upload/update/delete)
- ✅ Attendance reports and analytics
- ✅ Admin audit logs
---

## 📁 Project Structure

```
College_Portal/
├── Frontend/                          # React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx             # Login page
│   │   │   ├── student/
│   │   │   │   └── SimpleStudentDashboard.jsx  # Main student interface
│   │   │   └── admin/
│   │   │       └── CompleteAdminDashboard.jsx  # Main admin interface
│   │   ├── api/
│   │   │   └── client.js             # API configuration & endpoints
│   │   ├── store/
│   │   │   └── authStore.js          # Auth state management
│   │   ├── App.jsx                   # Main app component
│   │   └── main.jsx                  # Entry point
│   ├── index.html                    # HTML template
│   ├── package.json                  # NPM dependencies
│   ├── vite.config.js                # Vite configuration
│   └── tailwind.config.js            # Tailwind CSS config
│
├── Backend/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py                   # Main FastAPI app
│   │   ├── database.py               # Database configuration
│   │   ├── models.py                 # Database models (tables)
│   │   ├── schemas.py                # Pydantic schemas (validation)
│   │   ├── core/
│   │   │   ├── config.py             # Configuration & env vars
│   │   │   └── security.py           # JWT & password utilities
│   │   ├── routers/                  # API endpoints
│   │   │   ├── auth.py               # Authentication routes
│   │   │   ├── student.py            # Student routes
│   │   │   ├── admin.py              # Admin routes
│   │   │   ├── assignment.py         # Assignment routes
│   │   │   ├── attendance.py         # Attendance routes
│   │   │   ├── content.py            # Content/materials routes
│   │   │   └── quiz.py               # Quiz routes
│   │   └── services/
│   │       ├── academic_service.py   # Business logic
│   │       ├── admin_service.py      # Admin operations
│   │       ├── analytics_service.py  # Analytics & reports
│   │       └── student_service.py    # Student operations
│   ├── .env                          # Environment variables
│   ├── requirements.txt              # Python dependencies
│   ├── create_test_data.py           # Setup script
│   └── run_backend.py                # Start backend
│
├── .venv/                            # Python virtual environment
├── README.md                         # This file
└── test_api.py                       # API testing script
```

---

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.11+ installed
- Node.js 16+ installed
- npm installed

### **Step 1: Navigate to Project**

```bash
cd d:\Clg
```

### **Step 2: Setup Python Backend**

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r Backend/requirements.txt
```

### **Step 3: Setup Frontend**

```bash
cd Frontend
npm install
cd ..
```

### **Step 4: Setup Database & Test Data**

```bash
cd Backend
python create_test_data.py
cd ..
```

You should see:
```
✅ TEST DATA CREATED SUCCESSFULLY!
```

---

## ▶️ Running the Project

### **Terminal 1 - Start Backend:**

```bash
cd d:\Clg
.venv\Scripts\Activate.ps1
cd Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Terminal 2 - Start Frontend:**

```bash
cd d:\Clg\Frontend
npm run dev
```

**Expected output:**
```
VITE v5.4.21 ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

---

## 🎯 Access the Application

Once both servers are running:

1. **Open:** `http://localhost:5173`
2. **Login with:**
   - Email: `student1@college.com`
   - Password: `student123`

Or admin:
   - Email: `admin@college.com`
   - Password: `admin123`

---

## 🔐 Test Credentials

### **Admin Account**
```
Email: admin@college.com
Password: admin123
```

### **Student Accounts**
```
Student 1:
  Email: student1@college.com
  Password: student123
  Name: Raj Kumar
  Year: 3
  Department: CSE

Student 2:
  Email: student2@college.com
  Password: student123
  Name: Priya Singh
  Year: 4
  Department: CSE

Student 3:
  Email: student3@college.com
  Password: student123
  Name: Arjun Patel
  Year: 5
  Department: ECE

Student 4:
  Email: student4@college.com
  Password: student123
  Name: Neha Sharma
  Year: 6
  Department: CSE
```

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:8000/api`

### **Authentication**
- `POST /auth/login` - Login
- `POST /auth/register` - Register user
- `POST /auth/validate-token` - Validate token

### **Student Routes**
- `GET /student/dashboard` - Get dashboard
- `GET /student/assignments` - Get assignments
- `GET /student/quizzes` - Get quizzes
- `GET /student/attendance` - Get attendance
- `GET /student/marks` - Get marks
- `GET /student/notifications` - Get notifications

### **Admin Routes**
- `GET /admin/dashboard` - Get dashboard stats
- `GET /admin/students` - List students
- `POST /admin/attendance/mark` - Mark attendance
- `POST /admin/marks/update` - Update marks

**Full docs:** `http://localhost:8000/docs`

---

## 💾 Database

### **Type:** SQLite
### **Location:** `Backend/college_portal.db`

### **Tables:**
- users, students, student_progress
- academic_years, academic_content
- assignments, student_assignments
- quizzes, quiz_questions, student_quizzes
- attendance, student_marks
- notifications, todo_reminders

### **Reset Database:**
```bash
cd Backend
python create_test_data.py
```

---

## 📞 Common Commands

### **Backend**
```bash
# Start server
python -m uvicorn app.main:app --reload

# Reset database
python create_test_data.py

# Test API
python test_api.py

# Activate venv
.venv\Scripts\Activate.ps1
```

### **Frontend**
```bash
# Start dev server
npm run dev

# Build production
npm run build

# Install dependencies
npm install
```

---

## 🐛 Troubleshooting

### **Backend won't start - "Address already in use"**
```bash
# Try different port
python -m uvicorn app.main:app --port 8001
```

### **Frontend shows blank page**
```bash
# Hard refresh browser
Ctrl + Shift + R

# Clear cache
Ctrl + Shift + Delete
```

### **Login fails**
```bash
# Reload test data
cd Backend
python create_test_data.py
```

### **CORS error**
```bash
# Verify backend is running
http://localhost:8000/docs

# Check browser console for details (F12)
```

### **Database issues**
```bash
# Delete and recreate
cd Backend
python create_test_data.py
```

---

## ✅ Quick Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 16+ installed
- [ ] Virtual environment created
- [ ] Python dependencies installed
- [ ] NPM dependencies installed
- [ ] Test data loaded
- [ ] Ports 8000 & 5173 available

---

**Access the app at:** `http://localhost:5173`  
**API docs at:** `http://localhost:8000/docs`

Happy Learning! 🎓✨
