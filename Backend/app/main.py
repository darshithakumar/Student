from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_router, student_router, admin_router, attendance_router, content_router, assignment_router, quiz_router, ai_router
from fastapi import WebSocket, WebSocketDisconnect
from app.core.websockets import manager

app = FastAPI(
    title="College Academic Portal",
    description="Automated academic portal for students and administrators",
    version="1.0.0"
)

from app.core.config import FRONTEND_URL

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
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
app.include_router(ai_router)

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

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
