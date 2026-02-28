"""
Quiz Router
Endpoints for quiz management, question handling, and student responses
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
import json

from app.database import SessionLocal
from app.models import (
    Quiz, QuizQuestion, StudentQuiz, Student, User, AdminLog, Notification,
    AcademicYear, StudentMarks
)
from app.schemas import QuizCreate, QuizQuestionCreate, StudentQuizSubmit
from app.core.security import verify_token
from app.services.academic_service import AcademicService

router = APIRouter(tags=["quizzes"])

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
async def create_quiz(
    quiz_data: QuizCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new quiz"""
    new_quiz = Quiz(
        academic_year_id=quiz_data.academic_year_id,
        subject_name=quiz_data.subject_name,
        title=quiz_data.title,
        description=quiz_data.description,
        max_marks=quiz_data.max_marks,
        duration_minutes=quiz_data.duration_minutes,
        start_time=quiz_data.start_time,
        end_time=quiz_data.end_time,
        created_by=admin.id
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    # Get students for this year and create student quizzes
    academic_year = db.query(AcademicYear).filter(
        AcademicYear.id == quiz_data.academic_year_id
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
                student_quiz = StudentQuiz(
                    quiz_id=new_quiz.id,
                    student_id=student.user_id,
                    status="not_started"
                )
                db.add(student_quiz)
                
                # Create notification
                AcademicService.create_notification(
                    db,
                    student.user_id,
                    f"New Quiz: {quiz_data.title}",
                    f"A new quiz '{quiz_data.title}' is available. Duration: {quiz_data.duration_minutes} minutes",
                    "quiz",
                    new_quiz.id
                )
        
        db.commit()
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="create",
        entity_type="quiz",
        entity_id=new_quiz.id,
        changes={
            "subject": quiz_data.subject_name,
            "title": quiz_data.title,
            "duration": quiz_data.duration_minutes
        }
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "message": "Quiz created successfully",
        "quiz_id": str(new_quiz.id),
        "students_notified": len(students) if academic_year else 0
    }

@router.post("/{quiz_id}/add-question")
async def add_question(
    quiz_id: UUID,
    question_data: QuizQuestionCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Add a question to a quiz"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    new_question = QuizQuestion(
        quiz_id=quiz_id,
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        options=question_data.options,
        correct_answer=question_data.correct_answer,
        marks=question_data.marks,
        order=question_data.order
    )
    
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    return {
        "message": "Question added successfully",
        "question_id": str(new_question.id)
    }

@router.put("/{quiz_id}/update-question/{question_id}")
async def update_question(
    quiz_id: UUID,
    question_id: UUID,
    question_data: QuizQuestionCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update a quiz question"""
    question = db.query(QuizQuestion).filter(
        QuizQuestion.id == question_id,
        QuizQuestion.quiz_id == quiz_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    question.question_text = question_data.question_text
    question.question_type = question_data.question_type
    question.options = question_data.options
    question.correct_answer = question_data.correct_answer
    question.marks = question_data.marks
    question.order = question_data.order
    
    db.commit()
    
    return {"message": "Question updated successfully"}

@router.delete("/{quiz_id}/delete-question/{question_id}")
async def delete_question(
    quiz_id: UUID,
    question_id: UUID,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete a quiz question"""
    question = db.query(QuizQuestion).filter(
        QuizQuestion.id == question_id,
        QuizQuestion.quiz_id == quiz_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    db.delete(question)
    db.commit()
    
    return {"message": "Question deleted successfully"}

@router.get("/all")
async def get_all_quizzes(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all quizzes"""
    quizzes = db.query(Quiz).all()
    
    return {
        "quizzes": [
            {
                "id": str(q.id),
                "subject": q.subject_name,
                "title": q.title,
                "duration": q.duration_minutes,
                "start_time": q.start_time.isoformat() if q.start_time else None,
                "end_time": q.end_time.isoformat() if q.end_time else None,
                "max_marks": q.max_marks
            }
            for q in quizzes
        ],
        "total": len(quizzes)
    }

@router.get("/{quiz_id}/responses")
async def get_quiz_responses(
    quiz_id: UUID,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all student responses for a quiz"""
    responses = db.query(StudentQuiz).filter(
        StudentQuiz.quiz_id == quiz_id
    ).all()
    
    return {
        "responses": [
            {
                "id": str(r.id),
                "student_id": str(r.student_id),
                "status": r.status,
                "marks_obtained": r.marks_obtained,
                "start_time": r.start_time.isoformat() if r.start_time else None,
                "end_time": r.end_time.isoformat() if r.end_time else None
            }
            for r in responses
        ],
        "total": len(responses),
        "submitted": sum(1 for r in responses if r.status == "submitted"),
        "graded": sum(1 for r in responses if r.marks_obtained)
    }

# ==================== STUDENT ENDPOINTS ====================

@router.get("/my-quizzes")
async def get_my_quizzes(
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Get all quizzes available for the student"""
    student_quizzes = db.query(StudentQuiz).filter(
        StudentQuiz.student_id == current_user.id
    ).all()
    
    return {
        "quizzes": [
            {
                "id": str(sq.id),
                "quiz_id": str(sq.quiz_id),
                "status": sq.status,
                "marks_obtained": sq.marks_obtained,
                "start_time": sq.start_time.isoformat() if sq.start_time else None,
                "end_time": sq.end_time.isoformat() if sq.end_time else None
            }
            for sq in student_quizzes
        ],
        "total": len(student_quizzes)
    }

@router.post("/{quiz_id}/start")
async def start_quiz(
    quiz_id: UUID,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Start a quiz"""
    student_quiz = db.query(StudentQuiz).filter(
        StudentQuiz.quiz_id == quiz_id,
        StudentQuiz.student_id == current_user.id
    ).first()
    
    if not student_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not assigned to you"
        )
    
    if student_quiz.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz already submitted"
        )
    
    student_quiz.status = "in_progress"
    student_quiz.start_time = datetime.utcnow()
    db.commit()
    
    # Get quiz questions
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).order_by(QuizQuestion.order).all()
    
    return {
        "message": "Quiz started",
        "quiz_id": str(quiz_id),
        "questions": [
            {
                "id": str(q.id),
                "question": q.question_text,
                "type": q.question_type,
                "options": q.options,
                "marks": q.marks,
                "order": q.order
            }
            for q in questions
        ]
    }

@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: UUID,
    submission_data: StudentQuizSubmit,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Submit quiz answers"""
    student_quiz = db.query(StudentQuiz).filter(
        StudentQuiz.quiz_id == quiz_id,
        StudentQuiz.student_id == current_user.id
    ).first()
    
    if not student_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if student_quiz.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz already submitted"
        )
    
    # Grade the quiz
    student_quiz.answers = json.dumps(
        [{"question_id": str(a.question_id), "answer": a.answer} for a in submission_data.answers]
    )
    
    marks_obtained = 0
    for answer in submission_data.answers:
        question = db.query(QuizQuestion).filter(
            QuizQuestion.id == answer.question_id
        ).first()
        
        if question and question.correct_answer == answer.answer:
            marks_obtained += question.marks
    
    student_quiz.marks_obtained = marks_obtained
    student_quiz.status = "submitted"
    student_quiz.end_time = datetime.utcnow()
    db.commit()
    
    # Create notification
    AcademicService.create_notification(
        db,
        current_user.id,
        "Quiz Submitted",
        f"Your quiz has been submitted. Marks: {marks_obtained}",
        "quiz",
        quiz_id
    )
    
    return {
        "message": "Quiz submitted successfully",
        "marks_obtained": marks_obtained
    }

@router.get("/{quiz_id}/details")
async def get_quiz_details(
    quiz_id: UUID,
    current_user: User = Depends(verify_student),
    db: Session = Depends(get_db)
):
    """Get quiz details"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return {
        "id": str(quiz.id),
        "subject": quiz.subject_name,
        "title": quiz.title,
        "description": quiz.description,
        "duration": quiz.duration_minutes,
        "max_marks": quiz.max_marks,
        "start_time": quiz.start_time.isoformat() if quiz.start_time else None,
        "end_time": quiz.end_time.isoformat() if quiz.end_time else None
    }
