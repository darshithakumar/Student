# 🎓 Student Academic Portal

A modern, automated college academic portal that dynamically delivers year-based content to students and provides powerful management tools for administrators.

## 🌟 Features

### 🧑‍🎓 Student Interface
- **Dynamic Content Delivery:** Automatically detects the student's batch year and current academic year to serve relevant Notes, PPTs, Textbooks, and PYQs (Previous Year Questions).
- **AI Study Assistant:** A built-in AI assistant that analyzes your GPA, pending assignments, and attendance to provide personalized study insights.
- **Academic Tracking:** View real-time attendance, track GPA progression, and submit assignments and quizzes natively in the browser.
- **To-Do List:** Built-in task manager for tracking upcoming deadlines.

### 👨‍💼 Administrator Interface
- **Automated Year Progression:** Students automatically progress to the next academic year without manual intervention (with options for manual overrides).
- **Student Management:** View student lists, track individual academic progress, and monitor attendance metrics.
- **Content Management:** Upload and distribute academic content (PDFs, PPTs, etc.) organized by year and department.
- **AI Admin Assistant:** Get automated insights on low-attendance students and pending grading tasks.

## 🚀 Tech Stack

### Frontend
- **Framework:** React + Vite
- **Styling:** Tailwind CSS (Glassmorphism & Modern UI)
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (Hosted on Neon)
- **Authentication:** JWT & Bcrypt Password Hashing
- **Deployment:** Render

---

## 💻 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/darshithakumar/Student.git
cd Student
```

### 2. Backend Setup
```bash
cd Backend
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file in the Backend directory and add:
# DATABASE_URL=postgresql://username:password@host/dbname
# SECRET_KEY=your_super_secret_key
# FRONTEND_URL=http://localhost:5173

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
# Open a new terminal tab
cd Frontend

# Install dependencies
npm install

# Set up environment variables
# Create a .env file in the Frontend directory and add:
# VITE_API_URL=http://localhost:8000/api

# Run the frontend server
npm run dev
```

---

## 🌐 Production Deployment

This project is configured to be deployed easily using Render and Vercel.

1. **Deploy Backend (Render):**
   - Connect GitHub to Render as a Web Service.
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Ensure you set `DATABASE_URL` and `SECRET_KEY` in Render's environment variables.

2. **Deploy Frontend (Vercel):**
   - Connect GitHub to Vercel.
   - Set Framework Preset to **Vite**.
   - Add the `VITE_API_URL` environment variable pointing to your deployed Render URL (e.g., `https://your-backend.onrender.com/api`).

3. **Secure the Connection:**
   - Take your Vercel URL and add it to your Render backend's `FRONTEND_URL` environment variable to secure CORS.

---

## 🏗️ CI/CD Roadmap

The long-term infrastructure plan for this project involves transitioning to a full enterprise-grade CI/CD pipeline:
- **Docker:** Containerizing the frontend and backend for guaranteed environment consistency.
- **GitHub Actions / Jenkins:** Automated testing and Docker Image building upon every commit.
- **Kubernetes:** Orchestrating the containers for zero-downtime rollouts, auto-scaling, and self-healing.