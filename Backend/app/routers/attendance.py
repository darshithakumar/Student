"""
Attendance Router
Simplified endpoints for attendance operations
(More comprehensive attendance management available in admin and student routers)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from app.database import SessionLocal
from app.models import Attendance, User, Student
from app.schemas import AttendanceCreate
from app.core.security import verify_token
from app.services.academic_service import AcademicService

router = APIRouter(tags=["attendance"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_admin(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Verify that the user is an admin"""
    user = db.query(User).filter(User.id == token.get("sub")).first()
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an admin to access this resource"
        )
    return user

@router.post("/mark")
async def mark_attendance(
    data: AttendanceCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Mark attendance for a student"""
    AcademicService.record_attendance(
        db,
        data.student_id,
        data.date,
        data.present,
        admin.id
    )
    
    return {"message": "Attendance marked successfully"}

@router.get("/{student_id}")
async def get_attendance(
    student_id: UUID,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db),
    month: int = None,
    year: int = None
):
    """Get attendance for a student"""
    attendance = AcademicService.get_attendance_summary(db, student_id, month, year)
    
    return {
        "student_id": str(student_id),
        "month": attendance.month,
        "year": attendance.year,
        "total_classes": attendance.total_classes,
        "classes_attended": attendance.classes_attended,
        "attendance_percentage": attendance.attendance_percentage
    }
