"""
Assignment Router
Endpoints for assignment management and submission tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.database import SessionLocal
from app.models import (
    Assignment, StudentAssignment, Student, User, AdminLog,
    AcademicYear, Notification
)
from app.schemas import AssignmentCreate, StudentAssignmentResponse
from app.core.security import verify_token
from app.services.academic_service import AcademicService

router = APIRouter(tags=["assignments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to verify admin access
async def verify_admin(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Verify that the user is an admin"""
    user = db.query(User).filter(User.id == token.get("sub")).first()
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an admin to access this resource"
        )
    return user

async def verify_student(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Verify that the user is a student"""
    user = db.query(User).filter(User.id == token.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# ==================== ADMIN ENDPOINTS ====================

@router.post("/create")
async def create_assignment(
    assignment_data: AssignmentCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new assignment"""
    new_assignment = Assignment(
        academic_year_id=assignment_data.academic_year_id,
        subject_name=assignment_data.subject_name,
        title=assignment_data.title,
        description=assignment_data.description,
        instructions=assignment_data.instructions,
        file_url=assignment_data.file_url,
        due_date=assignment_data.due_date,
        max_marks=assignment_data.max_marks,
        created_by=admin.id
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    # Get students for this year and create student assignments
    academic_year = db.query(AcademicYear).filter(
        AcademicYear.id == assignment_data.academic_year_id
    ).first()
    
    if academic_year:
        students = db.query(Student).filter(
            Student.department == academic_year.department
        ).all()
        
        for student in students:
            # Check if student is in the correct year
            current_year = AcademicService.calculate_current_year(
                student.batch_year,
                student.current_year_override
            )
            
            if current_year == academic_year.year:
                student_assignment = StudentAssignment(
                    assignment_id=new_assignment.id,
                    student_id=student.user_id,
                    status="pending"
                )
                db.add(student_assignment)
                
                # Create notification
                AcademicService.create_notification(
                    db,
                    student.user_id,
                    f"New Assignment: {assignment_data.title}",
                    f"A new assignment '{assignment_data.title}' has been posted. Due: {assignment_data.due_date}",
                    "assignment",
                    new_assignment.id
                )
        
        db.commit()
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="create",
        entity_type="assignment",
        entity_id=new_assignment.id,
        changes={
            "subject": assignment_data.subject_name,
            "title": assignment_data.title,
            "due_date": str(assignment_data.due_date)
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "message": "Assignment created successfully",
        "assignment_id": str(new_assignment.id),
        "students_notified": len(students) if academic_year else 0
    }

@router.put("/update/{assignment_id}")
async def update_assignment(
    assignment_id: UUID,
    assignment_data: AssignmentCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Store old values
    old_values = {
        "title": assignment.title,
        "due_date": str(assignment.due_date)
    }
    
    assignment.subject_name = assignment_data.subject_name
    assignment.title = assignment_data.title
    assignment.description = assignment_data.description
    assignment.instructions = assignment_data.instructions
    assignment.file_url = assignment_data.file_url
    assignment.due_date = assignment_data.due_date
    assignment.max_marks = assignment_data.max_marks
    
    db.commit()
    db.refresh(assignment)
    
    # Notify students about the update
    student_assignments = db.query(StudentAssignment).filter(
        StudentAssignment.assignment_id == assignment_id
    ).all()
    
    for sa in student_assignments:
        AcademicService.create_notification(
            db,
            sa.student_id,
            f"Assignment Updated: {assignment.title}",
            f"The assignment '{assignment.title}' has been updated. New due date: {assignment.due_date}",
            "assignment",
            assignment_id
        )
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="update",
        entity_type="assignment",
        entity_id=assignment_id,
        changes={
            "old": old_values,
            "new": {
                "title": assignment.title,
                "due_date": str(assignment.due_date)
            }
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {"message": "Assignment updated successfully"}

@router.delete("/delete/{assignment_id}")
async def delete_assignment(
    assignment_id: UUID,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Delete student assignments
    student_assignments = db.query(StudentAssignment).filter(
        StudentAssignment.assignment_id == assignment_id
    ).all()
    
    for sa in student_assignments:
        db.delete(sa)
    
    db.delete(assignment)
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="delete",
        entity_type="assignment",
        entity_id=assignment_id,
        changes={"deleted": assignment.title}
    )
    db.add(log_entry)
    db.commit()
    
    return {"message": "Assignment deleted successfully"}

@router.get("/all")
async def get_all_assignments(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all assignments"""
    assignments = db.query(Assignment).all()
    
    return {
        "assignments": [
            {
                "id": str(a.id),
                "subject": a.subject_name,
                "title": a.title,
                "due_date": a.due_date.isoformat(),
                "max_marks": a.max_marks,
                "created_at": a.created_at.isoformat()
            }
            for a in assignments
        ],
        "total": len(assignments)
    }

@router.get("/submissions/{assignment_id}")
async def get_assignment_submissions(
    assignment_id: UUID,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all submissions for an assignment"""
    submissions = db.query(StudentAssignment).filter(
        StudentAssignment.assignment_id == assignment_id
    ).all()
    
    return {
        "submissions": [
            {
                "id": str(s.id),
                "student_id": str(s.student_id),
                "status": s.status,
                "submission_date": s.submission_date.isoformat() if s.submission_date else None,
                "marks_obtained": s.marks_obtained,
                "feedback": s.feedback
            }
            for s in submissions
        ],
        "total": len(submissions),
        "submitted": sum(1 for s in submissions if s.submission_date),
        "graded": sum(1 for s in submissions if s.status == "graded")
    }

# ==================== STUDENT ENDPOINTS ====================

@router.get("/my")
async def get_my_assignments(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Get all assignments for the current student"""
    student_assignments = db.query(StudentAssignment).filter(
        StudentAssignment.student_id == current_user.id
    ).all()
    
    return {
        "assignments": [
            {
                "id": str(sa.id),
                "assignment_id": str(sa.assignment_id),
                "status": sa.status,
                "submission_date": sa.submission_date.isoformat() if sa.submission_date else None,
                "marks_obtained": sa.marks_obtained,
                "feedback": sa.feedback
            }
            for sa in student_assignments
        ],
        "total": len(student_assignments)
    }

@router.get("/{assignment_id}/details")
async def get_assignment_details(
    assignment_id: UUID,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Get assignment details"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Get student's submission status
    student_assignment = db.query(StudentAssignment).filter(
        StudentAssignment.assignment_id == assignment_id,
        StudentAssignment.student_id == current_user.id
    ).first()
    
    return {
        "id": str(assignment.id),
        "subject": assignment.subject_name,
        "title": assignment.title,
        "description": assignment.description,
        "instructions": assignment.instructions,
        "file_url": assignment.file_url,
        "due_date": assignment.due_date.isoformat(),
        "max_marks": assignment.max_marks,
        "created_at": assignment.created_at.isoformat(),
        "submission_status": {
            "status": student_assignment.status if student_assignment else "not_found",
            "submission_date": student_assignment.submission_date.isoformat() if student_assignment and student_assignment.submission_date else None,
            "marks_obtained": student_assignment.marks_obtained if student_assignment else None,
            "feedback": student_assignment.feedback if student_assignment else None
        } if student_assignment else None
    }
