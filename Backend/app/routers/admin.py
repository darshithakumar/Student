"""
Admin Router
Endpoints for administrative operations (student tracking, attendance, marks, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from datetime import date

from app.database import SessionLocal
from app.models import (
    Student, StudentProgress, Attendance, StudentMarks, Assignment,
    StudentAssignment, User, AdminLog, Notification, Quiz, StudentQuiz
)
from app.schemas import (
    AttendanceCreate, StudentMarksCreate, BulkAttendanceUpdate,
    BulkMarksUpdate, AdminLogResponse
)
from app.core.security import verify_token
from app.services.academic_service import AcademicService

router = APIRouter(tags=["admin"])

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

# ==================== STUDENT TRACKING ====================

@router.get("/dashboard")
async def admin_dashboard(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Admin dashboard with system statistics"""
    total_students = db.query(func.count(Student.user_id)).scalar()
    total_assignments = db.query(func.count(Assignment.id)).scalar()
    total_quizzes = db.query(func.count(Quiz.id)).scalar()
    pending_submissions = db.query(func.count(StudentAssignment.id)).filter(
        StudentAssignment.status == "submitted"
    ).scalar()
    
    # Average attendance
    avg_attendance = db.query(func.avg(StudentProgress.gpa)).scalar() or 0.0
    
    return {
        "total_students": total_students,
        "total_assignments": total_assignments,
        "total_quizzes": total_quizzes,
        "pending_submissions": pending_submissions,
        "average_attendance": avg_attendance
    }

@router.get("/students")
async def get_all_students(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    department: str = None,
    batch_year: int = None
):
    """Get all students (with optional filters)"""
    query = db.query(Student)
    
    if department:
        query = query.filter(Student.department == department)
    if batch_year:
        query = query.filter(Student.batch_year == batch_year)
    
    students = query.all()
    
    return {
        "students": [
            {
                "user_id": str(s.user_id),
                "name": s.name,
                "batch_year": s.batch_year,
                "department": s.department,
                "current_year": AcademicService.calculate_current_year(
                    s.batch_year, s.current_year_override
                )
            }
            for s in students
        ],
        "total": len(students)
    }

@router.get("/students/{student_id}")
async def get_student_details(
    student_id: UUID,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a student"""
    student = db.query(Student).filter(Student.user_id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    progress = AcademicService.get_student_progress(db, student_id)
    attendance = AcademicService.get_attendance_summary(db, student_id)
    marks = AcademicService.get_consolidated_marks(db, student_id)
    
    current_year = AcademicService.calculate_current_year(
        student.batch_year, student.current_year_override
    )
    
    return {
        "student": {
            "user_id": str(student.user_id),
            "name": student.name,
            "batch_year": student.batch_year,
            "department": student.department,
            "current_year": current_year
        },
        "progress": {
            "gpa": progress.gpa,
            "total_assignments_completed": progress.total_assignments_completed,
            "total_quizzes_attempted": progress.total_quizzes_attempted
        },
        "attendance": {
            "total_classes": attendance.total_classes,
            "classes_attended": attendance.classes_attended,
            "attendance_percentage": attendance.attendance_percentage
        },
        "marks": marks
    }

# ==================== ATTENDANCE MANAGEMENT ====================

@router.post("/attendance/mark")
async def mark_attendance(
    attendance_record: AttendanceCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Mark attendance for a single student"""
    AcademicService.record_attendance(
        db,
        attendance_record.student_id,
        attendance_record.date,
        attendance_record.present,
        admin.id
    )
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="update",
        entity_type="attendance",
        entity_id=attendance_record.student_id,
        changes={
            "date": str(attendance_record.date),
            "present": attendance_record.present
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {"message": "Attendance marked successfully"}

@router.post("/attendance/bulk-mark")
async def mark_attendance_bulk(
    bulk_data: BulkAttendanceUpdate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Mark attendance for multiple students
    Useful for class attendance marking
    """
    AcademicService.mark_attendance_bulk(
        db,
        bulk_data.date,
        [
            {
                "student_id": record.student_id,
                "present": record.present
            }
            for record in bulk_data.attendance_records
        ],
        admin.id
    )
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="update",
        entity_type="attendance",
        changes={
            "bulk_update": True,
            "date": str(bulk_data.date),
            "total_records": len(bulk_data.attendance_records)
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "message": f"Attendance marked for {len(bulk_data.attendance_records)} students"
    }

@router.get("/attendance/{student_id}")
async def get_student_attendance(
    student_id: UUID,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    month: int = None,
    year: int = None
):
    """Get attendance record for a student"""
    attendance = AcademicService.get_attendance_summary(db, student_id, month, year)
    
    return {
        "student_id": str(student_id),
        "month": attendance.month,
        "year": attendance.year,
        "total_classes": attendance.total_classes,
        "classes_attended": attendance.classes_attended,
        "attendance_percentage": attendance.attendance_percentage
    }

# ==================== MARKS MANAGEMENT ====================

@router.post("/marks/update")
async def update_marks(
    marks_data: StudentMarksCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update marks for a student"""
    # Calculate percentage and grade
    percentage = (marks_data.marks_obtained / marks_data.max_marks) * 100
    
    # Simple grading logic (can be customized)
    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 60:
        grade = "D"
    else:
        grade = "F"
    
    student_marks = StudentMarks(
        student_id=marks_data.student_id,
        academic_year_id=marks_data.academic_year_id,
        subject_name=marks_data.subject_name,
        exam_type=marks_data.exam_type,
        marks_obtained=marks_data.marks_obtained,
        max_marks=marks_data.max_marks,
        percentage=percentage,
        grade=grade
    )
    
    db.add(student_marks)
    db.commit()
    db.refresh(student_marks)
    
    # Create notification for student
    AcademicService.create_notification(
        db,
        marks_data.student_id,
        f"Marks Updated: {marks_data.subject_name}",
        f"Your marks for {marks_data.subject_name} ({marks_data.exam_type}) have been updated. Grade: {grade}",
        "grade"
    )
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="create",
        entity_type="marks",
        entity_id=student_marks.id,
        changes={
            "subject": marks_data.subject_name,
            "exam_type": marks_data.exam_type,
            "marks": marks_data.marks_obtained,
            "grade": grade
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "message": "Marks updated successfully",
        "grade": grade,
        "percentage": percentage
    }

@router.post("/marks/bulk-update")
async def update_marks_bulk(
    bulk_data: BulkMarksUpdate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update marks for multiple students"""
    created_records = []
    
    for marks_data in bulk_data.marks_records:
        percentage = (marks_data.marks_obtained / marks_data.max_marks) * 100
        
        if percentage >= 90:
            grade = "A"
        elif percentage >= 80:
            grade = "B"
        elif percentage >= 70:
            grade = "C"
        elif percentage >= 60:
            grade = "D"
        else:
            grade = "F"
        
        student_marks = StudentMarks(
            student_id=marks_data.student_id,
            academic_year_id=marks_data.academic_year_id,
            subject_name=marks_data.subject_name,
            exam_type=marks_data.exam_type,
            marks_obtained=marks_data.marks_obtained,
            max_marks=marks_data.max_marks,
            percentage=percentage,
            grade=grade
        )
        
        db.add(student_marks)
        created_records.append(student_marks)
    
    db.commit()
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="create",
        entity_type="marks",
        changes={
            "bulk_update": True,
            "total_records": len(created_records)
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "message": f"Marks updated for {len(created_records)} records",
        "total_records": len(created_records)
    }

# ==================== ASSIGNMENT GRADING ====================

@router.get("/assignments/pending")
async def get_pending_assignments(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all pending submissions"""
    pending = db.query(StudentAssignment).filter(
        StudentAssignment.status == "submitted"
    ).all()
    
    return {
        "pending_submissions": [
            {
                "id": str(a.id),
                "student_id": str(a.student_id),
                "assignment_id": str(a.assignment_id),
                "submission_date": a.submission_date.isoformat() if a.submission_date else None,
                "status": a.status
            }
            for a in pending
        ],
        "total": len(pending)
    }

@router.post("/assignments/{assignment_id}/grade")
async def grade_assignment(
    assignment_id: UUID,
    student_id: UUID,
    marks: float,
    feedback: str = None,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Grade a submitted assignment"""
    student_assignment = db.query(StudentAssignment).filter(
        StudentAssignment.assignment_id == assignment_id,
        StudentAssignment.student_id == student_id
    ).first()
    
    if not student_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    student_assignment.marks_obtained = marks
    student_assignment.feedback = feedback
    student_assignment.status = "graded"
    student_assignment.graded_by = admin.id
    
    db.commit()
    db.refresh(student_assignment)
    
    # Create notification for student
    AcademicService.create_notification(
        db,
        student_id,
        "Assignment Graded",
        f"Your assignment has been graded. Marks: {marks}",
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
            "marks": marks,
            "feedback": feedback
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {"message": "Assignment graded successfully", "marks": marks}

# ==================== LOGS & ANALYTICS ====================

@router.get("/logs")
async def get_admin_logs(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """Get admin activity logs"""
    logs = db.query(AdminLog).order_by(
        AdminLog.timestamp.desc()
    ).limit(limit).all()
    
    return {
        "logs": [
            {
                "id": str(l.id),
                "admin_id": str(l.admin_id),
                "action": l.action,
                "entity_type": l.entity_type,
                "timestamp": l.timestamp.isoformat(),
                "changes": l.changes
            }
            for l in logs
        ],
        "total": len(logs)
    }

@router.get("/analytics/attendance-report")
async def get_attendance_report(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    department: str = None
):
    """Get attendance analytics for department"""
    # This can be expanded for more detailed analytics
    students = db.query(Student).all()
    
    if department:
        students = [s for s in students if s.department == department]
    
    attendance_data = []
    for student in students:
        attendance = AcademicService.get_attendance_summary(db, student.user_id)
        attendance_data.append({
            "student_id": str(student.user_id),
            "name": student.name,
            "attendance_percentage": attendance.attendance_percentage
        })
    
    return {
        "attendance_report": attendance_data,
        "total_students": len(attendance_data)
    }

@router.get("/health")
def admin_health():
    """Health check endpoint"""
    return {"status": "Admin API Running"}
