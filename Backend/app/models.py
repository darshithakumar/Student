from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Date, DateTime, Float, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import uuid
from datetime import datetime

# ==================== USER & AUTH MODELS ====================

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "student", "admin", "faculty"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== STUDENT MODELS ====================

class Student(Base):
    __tablename__ = "students"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    name = Column(String, nullable=False)
    batch_year = Column(Integer, nullable=False)  # Year joined (e.g., 2020, 2021)
    department = Column(String, nullable=False)
    current_year_override = Column(Integer)  # Optional: override calculated year
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index('idx_batch_department', 'batch_year', 'department'),)


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.user_id"), nullable=False, index=True)
    current_year = Column(Integer, nullable=False)  # Computed: current_year - batch_year
    gpa = Column(Float, default=0.0)
    total_assignments_completed = Column(Integer, default=0)
    total_quizzes_attempted = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== ACADEMIC CONTENT MODELS ====================

class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year = Column(Integer, nullable=False)  # 1, 2, 3, 4
    semester = Column(Integer, nullable=False)  # 1 or 2
    department = Column(String, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index('idx_year_semester_dept', 'year', 'semester', 'department'),)


class AcademicContent(Base):
    __tablename__ = "academic_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False)
    subject_name = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # "notes", "ppt", "textbook", "pyq", "demo_test"
    title = Column(String, nullable=False)
    description = Column(Text)
    file_url = Column(String, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)
    
    __table_args__ = (Index('idx_content_year_type', 'academic_year_id', 'content_type'),)


# ==================== ATTENDANCE MODELS ====================

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.user_id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    present = Column(Boolean, default=False)
    marked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # Admin who marked
    marked_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index('idx_attendance_student_date', 'student_id', 'date'),)


class AttendanceSummary(Base):
    __tablename__ = "attendance_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.user_id"), nullable=False, index=True)
    month = Column(Integer)  # Month (1-12)
    year = Column(Integer)  # Year
    total_classes = Column(Integer, default=0)
    classes_attended = Column(Integer, default=0)
    attendance_percentage = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== ASSIGNMENT MODELS ====================

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False)
    subject_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    file_url = Column(String)  # Assignment file/document
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    max_marks = Column(Integer, default=10)


class StudentAssignment(Base):
    __tablename__ = "student_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.user_id"), nullable=False, index=True)
    submission_file_url = Column(String)
    submission_date = Column(DateTime)
    status = Column(String, default="pending")  # "pending", "submitted", "graded"
    marks_obtained = Column(Float)
    feedback = Column(Text)
    graded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    graded_at = Column(DateTime)
    
    __table_args__ = (Index('idx_student_assignment', 'student_id', 'assignment_id'),)


# ==================== QUIZ MODELS ====================

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False)
    subject_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    max_marks = Column(Integer, default=10)
    duration_minutes = Column(Integer, default=30)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String)  # "mcq", "short_answer", "essay"
    options = Column(JSON)  # For MCQ: ["A", "B", "C", "D"]
    correct_answer = Column(String)
    marks = Column(Integer, default=1)
    order = Column(Integer)  # Question order


class StudentQuiz(Base):
    __tablename__ = "student_quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.user_id"), nullable=False, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String, default="in_progress")  # "in_progress", "submitted"
    marks_obtained = Column(Float)
    answers = Column(JSON)  # Store student's answers
    
    __table_args__ = (Index('idx_student_quiz', 'student_id', 'quiz_id'),)


# ==================== NOTIFICATION MODELS ====================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String)  # "assignment", "quiz", "grade", "attendance", "reminder"
    related_id = Column(UUID(as_uuid=True))  # ID of related entity
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== TODO/REMINDER MODELS ====================

class TodoReminder(Base):
    __tablename__ = "todo_reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    task_title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    priority = Column(String, default="medium")  # "low", "medium", "high"
    category = Column(String)  # "assignment", "quiz", "study", "personal"
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index('idx_todo_user_completed', 'user_id', 'is_completed'),)


# ==================== MARKS/GRADE MODELS ====================

class StudentMarks(Base):
    __tablename__ = "student_marks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.user_id"), nullable=False, index=True)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"))
    subject_name = Column(String, nullable=False)
    exam_type = Column(String)  # "assignment", "quiz", "midterm", "final"
    marks_obtained = Column(Float)
    max_marks = Column(Float, default=100.0)
    percentage = Column(Float)
    grade = Column(String)  # "A", "B", "C", "D", "F"
    recorded_date = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index('idx_marks_student_year', 'student_id', 'academic_year_id'),)


# ==================== ADMIN LOG MODELS ====================

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # "create", "update", "delete"
    entity_type = Column(String)  # "content", "assignment", "marks", "attendance"
    entity_id = Column(UUID(as_uuid=True))
    changes = Column(JSON)  # Track what changed
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index('idx_admin_log_timestamp', 'timestamp'),)
