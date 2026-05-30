"""
Student Router
Main endpoints for student interface (dashboard, assignments, quizzes, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, date

from app.database import SessionLocal
from app.models import (
    Student, StudentAssignment, StudentQuiz, Notification, 
    TodoReminder, User, Assignment, Quiz
)
from app.schemas import (
    StudentDashboardResponse, TodoReminderCreate, TodoReminderUpdate,
    StudentAssignmentSubmit, StudentAssignmentResponse, NotificationResponse,
    TodoReminderResponse
)
from app.core.security import verify_token
from app.services.academic_service import AcademicService

router = APIRouter(tags=["student"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to verify student access
async def verify_student(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Verify that the user is a student"""
    user = db.query(User).filter(User.id == token.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.get("/dashboard")
async def get_student_dashboard(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """
    MAIN STUDENT DASHBOARD
    
    ⚡ CORE AUTOMATION:
    - Automatically calculates current year based on batch_year
    - Returns ONLY year-specific content
    - Student sees the exact materials they need without searching
    
    Example:
    - 2020 batch in 2026 login → See 1st year materials (2026-2020+1=7, capped at 4 = 4)
    - 2020 batch in 2024 login → See 2nd year materials (2024-2020+1=5, capped at 4 = 4)
    """
    dashboard_data = AcademicService.get_student_dashboard(db, current_user.id)
    
    if not dashboard_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return {
        "student_id": str(current_user.id),
        "name": dashboard_data["student"].name,
        "department": dashboard_data["student"].department,
        "batch_year": dashboard_data["student"].batch_year,
        "current_year": dashboard_data["current_year"],
        "academic_content": dashboard_data["academic_content"],
        "assignments": dashboard_data["assignments"],
        "quizzes": dashboard_data["quizzes"],
        "progress": {
            "gpa": dashboard_data["progress"].gpa,
            "total_assignments_completed": dashboard_data["progress"].total_assignments_completed,
            "total_quizzes_attempted": dashboard_data["progress"].total_quizzes_attempted
        },
        "attendance": {
            "total_classes": dashboard_data["attendance"].total_classes,
            "classes_attended": dashboard_data["attendance"].classes_attended,
            "attendance_percentage": dashboard_data["attendance"].attendance_percentage
        },
        "consolidated_marks": dashboard_data["marks"],
        "notifications": [
            {
                "id": str(n.id),
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "created_at": n.created_at.isoformat()
            }
            for n in dashboard_data["notifications"]
        ],
        "todo_reminders": [
            {
                "id": str(t.id),
                "task": t.task_title,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "completed": t.is_completed
            }
            for t in dashboard_data["todo_reminders"]
        ]
    }

@router.get("/assignments")
async def get_my_assignments(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Get all assignments for the student with full assignment details"""
    pending_assignments = db.query(StudentAssignment).filter(
        StudentAssignment.student_id == current_user.id
    ).all()
    
    result = []
    for a in pending_assignments:
        assignment = db.query(Assignment).filter(Assignment.id == a.assignment_id).first()
        if assignment:
            result.append({
                "id": str(a.id),
                "assignment_id": str(a.assignment_id),
                "title": assignment.title,
                "subject_name": assignment.subject_name,
                "description": assignment.description,
                "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                "max_marks": assignment.max_marks,
                "status": a.status,
                "submission_date": a.submission_date.isoformat() if a.submission_date else None,
                "marks_obtained": a.marks_obtained,
                "feedback": a.feedback
            })
    
    return {
        "assignments": result,
        "total": len(result)
    }

@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: UUID,
    submission: StudentAssignmentSubmit,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Submit an assignment"""
    student_assignment = db.query(StudentAssignment).filter(
        StudentAssignment.assignment_id == assignment_id,
        StudentAssignment.student_id == current_user.id
    ).first()
    
    if not student_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    student_assignment.submission_file_url = submission.submission_file_url
    student_assignment.submission_date = datetime.utcnow()
    student_assignment.status = "submitted"
    
    db.commit()
    db.refresh(student_assignment)
    
    # Create notification for student
    AcademicService.create_notification(
        db,
        current_user.id,
        "Assignment Submitted",
        "Your assignment has been submitted successfully",
        "assignment",
        student_assignment.assignment_id
    )
    
    return {
        "message": "Assignment submitted successfully",
        "submission_date": student_assignment.submission_date.isoformat()
    }

@router.get("/quizzes")
async def get_my_quizzes(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Get all quizzes for the student with full quiz details"""
    pending_quizzes = db.query(StudentQuiz).filter(
        StudentQuiz.student_id == current_user.id
    ).all()
    
    result = []
    for sq in pending_quizzes:
        quiz = db.query(Quiz).filter(Quiz.id == sq.quiz_id).first()
        if quiz:
            result.append({
                "id": str(sq.id),
                "quiz_id": str(sq.quiz_id),
                "title": quiz.title,
                "subject_name": quiz.subject_name,
                "description": quiz.description,
                "duration_minutes": quiz.duration_minutes,
                "max_marks": quiz.max_marks,
                "start_time": quiz.start_time.isoformat() if quiz.start_time else None,
                "end_time": quiz.end_time.isoformat() if quiz.end_time else None,
                "status": sq.status,
                "marks_obtained": sq.marks_obtained
            })
    
    return {
        "quizzes": result,
        "total": len(result)
    }

@router.get("/attendance")
async def get_my_attendance(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db),
    month: int = None,
    year: int = None
):
    """Get attendance summary"""
    attendance = AcademicService.get_attendance_summary(
        db, current_user.id, month, year
    )
    
    return {
        "month": attendance.month,
        "year": attendance.year,
        "total_classes": attendance.total_classes,
        "classes_attended": attendance.classes_attended,
        "attendance_percentage": attendance.attendance_percentage
    }

@router.get("/marks")
async def get_my_marks(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Get consolidated marks for the student"""
    marks = AcademicService.get_consolidated_marks(db, current_user.id)
    return marks

@router.get("/notifications")
async def get_notifications(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db),
    unread_only: bool = False
):
    """Get notifications"""
    if unread_only:
        notifications = AcademicService.get_unread_notifications(db, current_user.id)
    else:
        notifications = db.query(Notification).filter(
            Notification.recipient_id == current_user.id
        ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return {
        "notifications": [
            {
                "id": str(n.id),
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ],
        "total": len(notifications)
    }

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    AcademicService.mark_notification_as_read(db, notification_id)
    return {"message": "Notification marked as read"}

@router.get("/todos")
async def get_my_todos(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Get all TODO reminders"""
    todos = db.query(TodoReminder).filter(
        TodoReminder.user_id == current_user.id
    ).order_by(TodoReminder.due_date).all()
    
    return {
        "todos": [
            {
                "id": str(t.id),
                "task": t.task_title,
                "description": t.description,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "priority": t.priority,
                "category": t.category,
                "completed": t.is_completed,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None
            }
            for t in todos
        ],
        "total": len(todos)
    }

@router.post("/todos")
async def create_todo(
    todo_data: TodoReminderCreate,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Create a new TODO reminder"""
    new_todo = TodoReminder(
        user_id=current_user.id,
        task_title=todo_data.task_title,
        description=todo_data.description,
        due_date=todo_data.due_date,
        priority=todo_data.priority,
        category=todo_data.category
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    
    return {
        "id": str(new_todo.id),
        "task": new_todo.task_title,
        "message": "TODO reminder created successfully"
    }

@router.put("/todos/{todo_id}")
async def update_todo(
    todo_id: UUID,
    todo_data: TodoReminderUpdate,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Update a TODO reminder"""
    todo = db.query(TodoReminder).filter(
        TodoReminder.id == todo_id,
        TodoReminder.user_id == current_user.id
    ).first()
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO not found"
        )
    
    if todo_data.task_title:
        todo.task_title = todo_data.task_title
    if todo_data.description:
        todo.description = todo_data.description
    if todo_data.due_date:
        todo.due_date = todo_data.due_date
    if todo_data.priority:
        todo.priority = todo_data.priority
    if todo_data.category:
        todo.category = todo_data.category
    if todo_data.is_completed is not None:
        todo.is_completed = todo_data.is_completed
        if todo_data.is_completed:
            todo.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)
    
    return {
        "id": str(todo.id),
        "task": todo.task_title,
        "description": todo.description,
        "due_date": todo.due_date.isoformat() if todo.due_date else None,
        "priority": todo.priority,
        "category": todo.category,
        "completed": todo.is_completed,
        "completed_at": todo.completed_at.isoformat() if todo.completed_at else None
    }

@router.patch("/todos/{todo_id}")
async def patch_todo(
    todo_id: UUID,
    todo_data: TodoReminderUpdate,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Partially update a TODO reminder (PATCH alias for PUT)"""
    return await update_todo(todo_id, todo_data, current_user, db)

@router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: UUID,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Delete a TODO reminder"""
    todo = db.query(TodoReminder).filter(
        TodoReminder.id == todo_id,
        TodoReminder.user_id == current_user.id
    ).first()
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO not found"
        )
    
    db.delete(todo)
    db.commit()
    
    return {"message": "TODO deleted successfully"}

