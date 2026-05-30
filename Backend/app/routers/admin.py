"""
Admin Router
Endpoints for administrative operations (student tracking, attendance, marks, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel

from app.database import SessionLocal
from app.models import (
    Student, StudentProgress, Attendance, StudentMarks, Assignment,
    StudentAssignment, User, AdminLog, Notification, Quiz, StudentQuiz
)
from app.schemas import (
    AttendanceCreate, StudentMarksCreate, BulkAttendanceUpdate,
    BulkMarksUpdate, AdminLogResponse, StudentYearOverrideUpdate
)
from app.core.security import verify_token
from app.services.academic_service import AcademicService

class GradeAssignmentRequest(BaseModel):
    student_id: UUID
    marks: float
    feedback: Optional[str] = None

class CreateAssignmentRequest(BaseModel):
    title: str
    description: Optional[str] = None
    subject_name: str
    due_date: str
    max_marks: int = 10

class CreateQuizRequest(BaseModel):
    title: str
    description: Optional[str] = None
    subject_name: str
    duration_minutes: int = 30
    max_marks: int = 10

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
                ),
                "gpa": AcademicService.get_student_progress(db, s.user_id).gpa,
                "attendance_percentage": AcademicService.get_attendance_summary(db, s.user_id).attendance_percentage
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

@router.put("/students/{student_id}/override-year")
async def override_student_year(
    student_id: UUID,
    override_data: StudentYearOverrideUpdate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Override the computed academic year for a student"""
    student = db.query(Student).filter(Student.user_id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student.current_year_override = override_data.current_year_override
    db.commit()
    db.refresh(student)
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="update",
        entity_type="student",
        entity_id=student.user_id,
        changes={
            "field": "current_year_override",
            "new_value": override_data.current_year_override
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "message": "Student year overridden successfully",
        "current_year_override": student.current_year_override
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
    grade_data: GradeAssignmentRequest,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Grade a submitted assignment"""
    student_assignment = db.query(StudentAssignment).filter(
        StudentAssignment.assignment_id == assignment_id,
        StudentAssignment.student_id == grade_data.student_id
    ).first()
    
    if not student_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    student_assignment.marks_obtained = grade_data.marks
    student_assignment.feedback = grade_data.feedback
    student_assignment.status = "graded"
    student_assignment.graded_by = admin.id
    
    db.commit()
    db.refresh(student_assignment)
    
    # Create notification for student
    AcademicService.create_notification(
        db,
        grade_data.student_id,
        "Assignment Graded",
        f"Your assignment has been graded. Marks: {grade_data.marks}",
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
            "marks": grade_data.marks,
            "feedback": grade_data.feedback
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {"message": "Assignment graded successfully", "marks": grade_data.marks}

@router.post("/assignments")
async def create_assignment_admin(
    assignment_data: CreateAssignmentRequest,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new assignment (simple version without academic_year_id)"""
    from datetime import datetime
    new_assignment = Assignment(
        subject_name=assignment_data.subject_name,
        title=assignment_data.title,
        description=assignment_data.description,
        due_date=datetime.fromisoformat(assignment_data.due_date) if assignment_data.due_date else None,
        max_marks=assignment_data.max_marks,
        created_by=admin.id
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    log_entry = AdminLog(
        admin_id=admin.id,
        action="create",
        entity_type="assignment",
        entity_id=new_assignment.id,
        changes={"title": new_assignment.title, "subject": new_assignment.subject_name}
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "id": str(new_assignment.id),
        "title": new_assignment.title,
        "subject_name": new_assignment.subject_name,
        "description": new_assignment.description,
        "due_date": new_assignment.due_date.isoformat() if new_assignment.due_date else None,
        "max_marks": new_assignment.max_marks
    }

@router.post("/quizzes")
async def create_quiz_admin(
    quiz_data: CreateQuizRequest,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new quiz (simple version without academic_year_id)"""
    new_quiz = Quiz(
        subject_name=quiz_data.subject_name,
        title=quiz_data.title,
        description=quiz_data.description,
        duration_minutes=quiz_data.duration_minutes,
        max_marks=quiz_data.max_marks,
        created_by=admin.id
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    log_entry = AdminLog(
        admin_id=admin.id,
        action="create",
        entity_type="quiz",
        entity_id=new_quiz.id,
        changes={"title": new_quiz.title, "subject": new_quiz.subject_name}
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "id": str(new_quiz.id),
        "title": new_quiz.title,
        "subject_name": new_quiz.subject_name,
        "description": new_quiz.description,
        "duration_minutes": new_quiz.duration_minutes,
        "max_marks": new_quiz.max_marks
    }

@router.post("/attendance")
async def mark_attendance_single(
    attendance_record: AttendanceCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Mark attendance for a single student (alias for /attendance/mark)"""
    AcademicService.record_attendance(
        db,
        attendance_record.student_id,
        attendance_record.date,
        attendance_record.present,
        admin.id
    )
    
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
