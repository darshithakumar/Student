from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from datetime import datetime

from app.database import SessionLocal
from app.models import (
    Student, StudentProgress, AttendanceSummary, User, Assignment,
    StudentAssignment, Quiz, StudentQuiz
)
from app.core.security import verify_token
from app.services.academic_service import AcademicService

router = APIRouter(prefix="/api/ai", tags=["ai"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependencies
async def verify_student(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == token.get("sub")).first()
    if not user or user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Must be a student")
    return user

async def verify_admin(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == token.get("sub")).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Must be an admin")
    return user

@router.get("/student-assistant")
async def student_assistant(student: User = Depends(verify_student), db: Session = Depends(get_db)):
    """Rule-based AI generating personalized study insights"""
    
    # 1. Analyze Attendance
    attendance = AcademicService.get_attendance_summary(db, student.id)
    attendance_message = ""
    if attendance.total_classes > 0:
        if attendance.attendance_percentage < 75:
            attendance_message = f"Warning: Your attendance is critically low at {attendance.attendance_percentage:.1f}%. Make sure to attend your upcoming classes!"
        elif attendance.attendance_percentage < 85:
            attendance_message = f"Your attendance is {attendance.attendance_percentage:.1f}%. Try to keep it above 85% to be safe."
        else:
            attendance_message = "Great job maintaining good attendance!"

    # 2. Analyze Pending Assignments
    pending_assignments = db.query(StudentAssignment).filter(
        StudentAssignment.student_id == student.id,
        StudentAssignment.status == "pending"
    ).all()
    
    assignment_message = ""
    if len(pending_assignments) > 0:
        assignment_message = f"You have {len(pending_assignments)} pending assignment(s) to complete. Prioritize them to keep your grades up."
    else:
        assignment_message = "You have no pending assignments right now. Enjoy your free time or review past notes!"
        
    # 3. Analyze Grades
    progress = AcademicService.get_student_progress(db, student.id)
    grade_message = ""
    if progress.gpa < 5.0:
        grade_message = "Your GPA is below average. Consider revising recent topics and attempting practice quizzes."
    elif progress.gpa >= 8.5:
        grade_message = "Excellent academic performance! Keep up the great work."
        
    insights = [attendance_message, assignment_message, grade_message]
    insights = [msg for msg in insights if msg]
    
    greeting = f"Hello! I am your AI Study Assistant. Here's your personalized briefing:\n\n"
    response_text = greeting + "\n\n".join(f"• {msg}" for msg in insights)
    
    if not insights:
        response_text = "You're all caught up! Keep doing your best."
        
    return {"message": response_text}


@router.get("/admin-assistant")
async def admin_assistant(admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Rule-based AI generating actionable insights for admins"""
    
    insights = []
    
    # 1. Identify low attendance students
    low_attendance_students = db.query(AttendanceSummary).filter(
        AttendanceSummary.attendance_percentage < 75.0,
        AttendanceSummary.total_classes >= 5
    ).count()
    
    if low_attendance_students > 0:
        insights.append(f"Action required: {low_attendance_students} students have attendance below 75%. Consider reaching out to them.")
        
    # 2. Identify pending grading
    pending_grading = db.query(StudentAssignment).filter(
        StudentAssignment.status == "submitted"
    ).count()
    
    if pending_grading > 0:
        insights.append(f"You have {pending_grading} student assignments waiting to be graded.")
        
    # 3. Low performing students
    low_gpa_students = db.query(StudentProgress).filter(
        StudentProgress.gpa < 5.0,
        StudentProgress.gpa > 0.0 # Ignore completely unassessed
    ).count()
    
    if low_gpa_students > 0:
        insights.append(f"Notice: {low_gpa_students} students have a GPA below 5.0. Additional academic support might be needed.")

    greeting = "Admin Briefing - Here are your actionable insights:\n\n"
    response_text = greeting + "\n\n".join(f"• {msg}" for msg in insights)
    
    if not insights:
        response_text = "System looks healthy! No urgent action items found."

    return {"message": response_text}

from pydantic import BaseModel

class AIChatRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_with_ai(request: AIChatRequest, token_data: dict = Depends(verify_token)):
    # Mock AI logic for now
    query_lower = request.query.lower()
    
    if "attendance" in query_lower:
        response_text = "I recommend checking your attendance tab. Keeping it above 85% is ideal."
    elif "gpa" in query_lower or "grade" in query_lower:
        response_text = "To improve your GPA, focus on completing pending assignments and taking practice quizzes."
    elif "assignment" in query_lower:
        response_text = "You can view and submit assignments in the Assignments tab."
    else:
        response_text = f"I am your AI assistant. You asked: '{request.query}'. I'm here to help you manage your academics better."
        
    return {"message": response_text}
