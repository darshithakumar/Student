from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_router, student_router, admin_router, attendance_router, content_router, assignment_router, quiz_router

app = FastAPI(
    title="College Academic Portal",
    description="Automated academic portal for students and administrators",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(student_router, prefix="/api/student")
app.include_router(admin_router, prefix="/api/admin")
app.include_router(attendance_router, prefix="/api/attendance")
app.include_router(content_router, prefix="/api/content")
app.include_router(assignment_router, prefix="/api/assignments")
app.include_router(quiz_router, prefix="/api/quizzes")

@app.get("/")
def root():
    return {
        "message": "College Academic Portal API",
        "status": "Running",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
