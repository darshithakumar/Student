"""
Academic Service: Core business logic for academic operations
Handles year calculation, content delivery, progress tracking, etc.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from app.models import (
    Student, StudentProgress, AcademicYear, AcademicContent,
    Assignment, StudentAssignment, Quiz, StudentQuiz, QuizQuestion,
    StudentMarks, Attendance, AttendanceSummary, Notification,
    TodoReminder, User
)


class AcademicService:
    """Service for handling academic operations"""

    @staticmethod
    def calculate_current_year(batch_year: int, override_year: Optional[int] = None) -> int:
        """
        Calculate the current academic year for a student
        
        Logic:
        - If override_year is set, use that
        - Otherwise: current_year = (current_year - batch_year) + 1
        - Example: batch_year=2020, current_year=2026 → 2026-2020+1 = 7
        - Cap at 4 (assuming 4-year course)
        
        Args:
            batch_year: Year the student joined (e.g., 2020)
            override_year: Optional override value
            
        Returns:
            Current academic year (1, 2, 3, or 4)
        """
        if override_year:
            return min(override_year, 4)
        
        current_year = datetime.now().year
        calculated_year = current_year - batch_year + 1
        
        # Cap at 4 for 4-year course (or modify as needed)
        return min(max(1, calculated_year), 4)

    @staticmethod
    def get_academic_year_record(
        db: Session,
        year: int,
        semester: int,
        department: str
    ) -> AcademicYear:
        """Get or create academic year record"""
        academic_year = db.query(AcademicYear).filter(
            and_(
                AcademicYear.year == year,
                AcademicYear.semester == semester,
                AcademicYear.department == department
            )
        ).first()
        
        if not academic_year:
            academic_year = AcademicYear(
                year=year,
                semester=semester,
                department=department
            )
            db.add(academic_year)
            db.commit()
            db.refresh(academic_year)
        
        return academic_year

    @staticmethod
    def get_content_by_year(
        db: Session,
        year: int,
        semester: int,
        department: str
    ) -> dict:
        """
        Fetch all academic content for a specific year
        This is the CORE AUTOMATION: Returns year-specific content
        
        Args:
            db: Database session
            year: Academic year (1, 2, 3, 4)
            semester: Semester (1 or 2)
            department: Department name
            
        Returns:
            Dictionary with organized content
        """
        # Get academic year record
        academic_year = AcademicService.get_academic_year_record(
            db, year, semester, department
        )
        
        # Fetch all content for this year
        content = db.query(AcademicContent).filter(
            AcademicContent.academic_year_id == academic_year.id
        ).all()
        
        # Organize content by type
        content_by_type = {
            "notes": [],
            "ppts": [],
            "textbooks": [],
            "pyqs": [],
            "demo_tests": []
        }
        
        for item in content:
            item_dict = {
                "id": str(item.id),
                "subject_name": item.subject_name,
                "title": item.title,
                "description": item.description,
                "file_url": item.file_url,
                "uploaded_at": item.uploaded_at.isoformat() if item.uploaded_at else None,
                "version": item.version
            }
            
            if item.content_type == "notes":
                content_by_type["notes"].append(item_dict)
            elif item.content_type == "ppt":
                content_by_type["ppts"].append(item_dict)
            elif item.content_type == "textbook":
                content_by_type["textbooks"].append(item_dict)
            elif item.content_type == "pyq":
                content_by_type["pyqs"].append(item_dict)
            elif item.content_type == "demo_test":
                content_by_type["demo_tests"].append(item_dict)
        
        return {
            "year": year,
            "semester": semester,
            **content_by_type
        }

    @staticmethod
    def get_assignments_for_year(
        db: Session,
        student_id: UUID,
        year: int,
        semester: int,
        department: str
    ) -> List[dict]:
        """Get all assignments for a student's current year"""
        academic_year = AcademicService.get_academic_year_record(
            db, year, semester, department
        )
        
        # Get assignments for this academic year
        assignments = db.query(StudentAssignment).join(
            Assignment, StudentAssignment.assignment_id == Assignment.id
        ).filter(
            and_(
                Assignment.academic_year_id == academic_year.id,
                StudentAssignment.student_id == student_id
            )
        ).all()
        
        return assignments

    @staticmethod
    def get_quizzes_for_year(
        db: Session,
        student_id: UUID,
        year: int,
        semester: int,
        department: str
    ) -> List[dict]:
        """Get all quizzes for a student's current year"""
        academic_year = AcademicService.get_academic_year_record(
            db, year, semester, department
        )
        
        quizzes = db.query(StudentQuiz).join(
            Quiz, StudentQuiz.quiz_id == Quiz.id
        ).filter(
            and_(
                Quiz.academic_year_id == academic_year.id,
                StudentQuiz.student_id == student_id
            )
        ).all()
        
        return quizzes

    @staticmethod
    def get_student_progress(
        db: Session,
        student_id: UUID
    ) -> StudentProgress:
        """Get or create student progress record"""
        progress = db.query(StudentProgress).filter(
            StudentProgress.student_id == student_id
        ).first()
        
        if not progress:
            progress = StudentProgress(student_id=student_id, current_year=1)
            db.add(progress)
            db.commit()
            db.refresh(progress)
        
        return progress

    @staticmethod
    def update_student_progress(
        db: Session,
        student_id: UUID,
        current_year: int
    ) -> StudentProgress:
        """Update student's current year and other progress metrics"""
        progress = AcademicService.get_student_progress(db, student_id)
        progress.current_year = current_year
        progress.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(progress)
        return progress

    @staticmethod
    def get_attendance_summary(
        db: Session,
        student_id: UUID,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> AttendanceSummary:
        """Get attendance summary for a student"""
        if not month:
            month = datetime.now().month
        if not year:
            year = datetime.now().year
        
        summary = db.query(AttendanceSummary).filter(
            and_(
                AttendanceSummary.student_id == student_id,
                AttendanceSummary.month == month,
                AttendanceSummary.year == year
            )
        ).first()
        
        # If not found, calculate from attendance records
        if not summary:
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            total_records = db.query(func.count(Attendance.id)).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.date >= start_date,
                    Attendance.date < end_date
                )
            ).scalar()
            
            present_records = db.query(func.count(Attendance.id)).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.present == True,
                    Attendance.date >= start_date,
                    Attendance.date < end_date
                )
            ).scalar()
            
            percentage = (present_records / total_records * 100) if total_records > 0 else 0.0
            
            summary = AttendanceSummary(
                student_id=student_id,
                month=month,
                year=year,
                total_classes=total_records,
                classes_attended=present_records,
                attendance_percentage=percentage
            )
            db.add(summary)
            db.commit()
        
        return summary

    @staticmethod
    def record_attendance(
        db: Session,
        student_id: UUID,
        date_val: date,
        present: bool,
        marked_by: UUID
    ) -> None:
        """Record attendance for a student"""
        existing = db.query(Attendance).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.date == date_val
            )
        ).first()
        
        if existing:
            existing.present = present
            existing.marked_by = marked_by
            existing.marked_at = datetime.utcnow()
        else:
            attendance = Attendance(
                student_id=student_id,
                date=date_val,
                present=present,
                marked_by=marked_by
            )
            db.add(attendance)
        
        db.commit()

    @staticmethod
    def mark_attendance_bulk(
        db: Session,
        date_val: date,
        attendance_records: List[dict],
        marked_by: UUID
    ) -> None:
        """Mark attendance for multiple students at once"""
        for record in attendance_records:
            AcademicService.record_attendance(
                db,
                record['student_id'],
                date_val,
                record['present'],
                marked_by
            )

    @staticmethod
    def get_consolidated_marks(
        db: Session,
        student_id: UUID,
        year: Optional[int] = None
    ) -> dict:
        """Get consolidated marks for a student"""
        query = db.query(StudentMarks).filter(
            StudentMarks.student_id == student_id
        )
        
        if year:
            query = query.filter(StudentMarks.academic_year_id == year)
        
        marks = query.all()
        
        # Calculate overall GPA
        total_percentage = sum(m.percentage for m in marks if m.percentage) / len(marks) if marks else 0
        
        return {
            "student_id": str(student_id),
            "overall_percentage": total_percentage,
            "marks_by_subject": marks,
            "total_records": len(marks)
        }

    @staticmethod
    def get_pending_assignments(
        db: Session,
        student_id: UUID
    ) -> List[StudentAssignment]:
        """Get pending assignments for a student"""
        pending = db.query(StudentAssignment).filter(
            and_(
                StudentAssignment.student_id == student_id,
                StudentAssignment.status.in_(["pending", "submitted"])
            )
        ).all()
        return pending

    @staticmethod
    def get_pending_quizzes(
        db: Session,
        student_id: UUID
    ) -> List[StudentQuiz]:
        """Get pending/in-progress quizzes for a student"""
        pending = db.query(StudentQuiz).filter(
            and_(
                StudentQuiz.student_id == student_id,
                StudentQuiz.status == "in_progress"
            )
        ).all()
        return pending

    @staticmethod
    def create_notification(
        db: Session,
        recipient_id: UUID,
        title: str,
        message: str,
        notification_type: str,
        related_id: Optional[UUID] = None
    ) -> Notification:
        """Create a notification for a user"""
        notification = Notification(
            recipient_id=recipient_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_unread_notifications(
        db: Session,
        user_id: UUID
    ) -> List[Notification]:
        """Get unread notifications for a user"""
        notifications = db.query(Notification).filter(
            and_(
                Notification.recipient_id == user_id,
                Notification.is_read == False
            )
        ).order_by(Notification.created_at.desc()).all()
        return notifications

    @staticmethod
    def mark_notification_as_read(
        db: Session,
        notification_id: UUID
    ) -> None:
        """Mark a notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        if notification:
            notification.is_read = True
            db.commit()

    @staticmethod
    def get_student_dashboard(
        db: Session,
        student_id: UUID
    ) -> dict:
        """
        MAIN DASHBOARD: Returns all data for student interface
        This is the core function that populates the student dashboard
        automatically based on their current year
        
        ⚡ KEY AUTOMATION LOGIC:
        - Fetches batch_year from student record
        - Calculates current_year automatically
        - Returns ONLY the academic content for that year
        - No manual filtering needed - it's all automatic!
        """
        # Get student info
        student = db.query(Student).filter(Student.user_id == student_id).first()
        user = db.query(User).filter(User.id == student_id).first()
        
        if not student:
            return None
        
        # Calculate current year - THIS IS THE CORE AUTOMATION
        current_year = AcademicService.calculate_current_year(
            student.batch_year,
            student.current_year_override
        )
        
        # Update student progress with current year
        AcademicService.update_student_progress(db, student_id, current_year)
        
        # Get all data organized by year
        content = AcademicService.get_content_by_year(
            db, current_year, 1, student.department
        )
        
        assignments = AcademicService.get_assignments_for_year(
            db, student_id, current_year, 1, student.department
        )
        
        quizzes = AcademicService.get_quizzes_for_year(
            db, student_id, current_year, 1, student.department
        )
        
        progress = AcademicService.get_student_progress(db, student_id)
        attendance = AcademicService.get_attendance_summary(db, student_id)
        marks = AcademicService.get_consolidated_marks(db, student_id)
        notifications = AcademicService.get_unread_notifications(db, student_id)
        pending_assignments = AcademicService.get_pending_assignments(db, student_id)
        
        # Get TODO reminders
        todos = db.query(TodoReminder).filter(
            and_(
                TodoReminder.user_id == student_id,
                TodoReminder.is_completed == False
            )
        ).order_by(TodoReminder.due_date).all()
        
        return {
            "student": student,
            "user": user,
            "current_year": current_year,
            "academic_content": content,
            "assignments": assignments,
            "quizzes": quizzes,
            "progress": progress,
            "attendance": attendance,
            "marks": marks,
            "notifications": notifications,
            "pending_assignments": pending_assignments,
            "todo_reminders": todos
        }
