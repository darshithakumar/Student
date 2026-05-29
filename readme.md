Project Overview
#  College Academic Portal

A full-stack academic management platform designed to streamline student and administrator operations within educational institutions.

## Features

### Student Module
- View assignments, quizzes, attendance, and marks
- Receive notifications and study materials
- Track academic progress

### Admin Module
- Manage students and academic records
- Upload assignments and study materials
- Monitor attendance and performance analytics

## Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite

### DevOps
- Docker
- Kubernetes
- Jenkins
- Docker Hub

## Test Credentials

### Admin Login

Email: admin@college.com
Password: admin123

### Student Login

Email: student1@college.com
Password: student123


## Run Locally

### Backend
cd Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python create_test_data.py
python -m uvicorn app.main:app --reload

### Frontend
cd Frontend
npm install
npm run dev

Frontend:
http://localhost:5173

Backend:
http://localhost:8000

API Docs:
http://localhost:8000/docs

##  Docker Deployment

Build Backend Image

docker build -t college-backend ./Backend

Build Frontend Image

docker build -t college-frontend ./Frontend

Run Backend

docker run -p 8000:8000 college-backend

Run Frontend

docker run -p 3000:80 college-frontend

## Kubernetes Deployment

Apply Resources

kubectl apply -f k8s/

Verify Pods

kubectl get pods

Verify Services

kubectl get svc

## Jenkins CI/CD

Pipeline Workflow

GitHub
   ↓
Jenkins
   ↓
Docker Build
   ↓
Docker Hub
   ↓
Kubernetes Deployment

The Jenkins pipeline automatically pulls source code from GitHub, builds Docker images, and deploys updated versions to Kubernetes.

## Architecture

Student/Admin
      ↓
React Frontend
      ↓
FastAPI Backend
      ↓
PostgreSQL Database
      ↓
Docker Containers
      ↓
Kubernetes Cluster
      ↓
Jenkins CI/CD


## Highlights

- Role-Based Authentication (Student/Admin)
- RESTful API Architecture
- Docker Containerization
- Kubernetes Orchestration
- Jenkins CI/CD Integration
- Responsive React Frontend
- PostgreSQL Database Integration
- Scalable Deployment Architecture