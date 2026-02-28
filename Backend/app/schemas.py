from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date, datetime
from typing import Optional, List, Any
from uuid import UUID

# ==================== AUTH SCHEMAS ====================

class RegisterSchema(BaseModel):
    email: str  # Changed from EmailStr due to validation issues
    password: str
    role: str  # "student", "admin", "faculty"
    name: str

class LoginSchema(BaseModel):
    email: str  # Changed from EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
    role: str

# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== STUDENT SCHEMAS ====================

class StudentBase(BaseModel):
    name: str
    batch_year: int
    department: str

class StudentCreate(StudentBase):
    user_id: UUID

class StudentResponse(StudentBase):
    user_id: UUID
    current_year_override: Optional[int]
    enrollment_date: datetime
    
    class Config:
        from_attributes = True

class StudentProgressResponse(BaseModel):
    id: UUID
    student_id: UUID
    current_year: int
    gpa: float
    total_assignments_completed: int
    total_quizzes_attempted: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

# ==================== ACADEMIC YEAR SCHEMAS ====================

class AcademicYearBase(BaseModel):
    year: int
    semester: int
    department: str
    start_date: datetime
    end_date: datetime

class AcademicYearCreate(AcademicYearBase):
    pass

class AcademicYearResponse(AcademicYearBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== ACADEMIC CONTENT SCHEMAS ====================

class AcademicContentBase(BaseModel):
    subject_name: str
    content_type: str  # "notes", "ppt", "textbook", "pyq", "demo_test"
    title: str
    description: Optional[str]
    file_url: str

class AcademicContentCreate(AcademicContentBase):
    academic_year_id: UUID

class AcademicContentResponse(AcademicContentBase):
    id: UUID
    academic_year_id: UUID
    uploaded_by: UUID
    uploaded_at: datetime
    version: int
    
    class Config:
        from_attributes = True

class ContentByYearResponse(BaseModel):
    year: int
    semester: int
    notes: List[AcademicContentResponse] = []
    ppts: List[AcademicContentResponse] = []
    textbooks: List[AcademicContentResponse] = []
    pyqs: List[AcademicContentResponse] = []
    demo_tests: List[AcademicContentResponse] = []

# ==================== ATTENDANCE SCHEMAS ====================

class AttendanceBase(BaseModel):
    student_id: UUID
    date: date
    present: bool

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: UUID
    marked_by: Optional[UUID]
    marked_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceSummaryResponse(BaseModel):
    id: UUID
    student_id: UUID
    month: int
    year: int
    total_classes: int
    classes_attended: int
    attendance_percentage: float
    last_updated: datetime
    
    class Config:
        from_attributes = True

# ==================== ASSIGNMENT SCHEMAS ====================

class AssignmentBase(BaseModel):
    subject_name: str
    title: str
    description: Optional[str]
    instructions: Optional[str]
    file_url: Optional[str]
    due_date: datetime
    max_marks: int = 10

class AssignmentCreate(AssignmentBase):
    academic_year_id: UUID

class AssignmentResponse(AssignmentBase):
    id: UUID
    academic_year_id: UUID
    created_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudentAssignmentBase(BaseModel):
    assignment_id: UUID
    student_id: UUID

class StudentAssignmentSubmit(BaseModel):
    submission_file_url: str

class StudentAssignmentUpdate(BaseModel):
    marks_obtained: float
    feedback: Optional[str]
    status: str

class StudentAssignmentResponse(BaseModel):
    id: UUID
    assignment_id: UUID
    student_id: UUID
    submission_file_url: Optional[str]
    submission_date: Optional[datetime]
    status: str
    marks_obtained: Optional[float]
    feedback: Optional[str]
    graded_by: Optional[UUID]
    graded_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ==================== QUIZ SCHEMAS ====================

class QuizBase(BaseModel):
    subject_name: str
    title: str
    description: Optional[str]
    max_marks: int = 10
    duration_minutes: int = 30
    start_time: datetime
    end_time: datetime

class QuizCreate(QuizBase):
    academic_year_id: UUID

class QuizResponse(QuizBase):
    id: UUID
    academic_year_id: UUID
    created_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str  # "mcq", "short_answer", "essay"
    options: Optional[List[str]]
    correct_answer: str
    marks: int = 1
    order: int

class QuizQuestionCreate(QuizQuestionBase):
    quiz_id: UUID

class QuizQuestionResponse(QuizQuestionBase):
    id: UUID
    quiz_id: UUID
    
    class Config:
        from_attributes = True

class StudentQuizBase(BaseModel):
    quiz_id: UUID
    student_id: UUID

class StudentQuizAnswer(BaseModel):
    question_id: UUID
    answer: str

class StudentQuizSubmit(BaseModel):
    answers: List[StudentQuizAnswer]

class StudentQuizResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    student_id: UUID
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    status: str
    marks_obtained: Optional[float]
    
    class Config:
        from_attributes = True

# ==================== NOTIFICATION SCHEMAS ====================

class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str  # "assignment", "quiz", "grade", "attendance", "reminder"
    related_id: Optional[UUID]

class NotificationCreate(NotificationBase):
    recipient_id: UUID

class NotificationResponse(NotificationBase):
    id: UUID
    recipient_id: UUID
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== TODO/REMINDER SCHEMAS ====================

class TodoReminderBase(BaseModel):
    task_title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: str = "medium"  # "low", "medium", "high"
    category: Optional[str]

class TodoReminderCreate(TodoReminderBase):
    pass

class TodoReminderUpdate(BaseModel):
    task_title: Optional[str]
    description: Optional[str]
    due_date: Optional[datetime]
    priority: Optional[str]
    category: Optional[str]
    is_completed: Optional[bool]

class TodoReminderResponse(TodoReminderBase):
    id: UUID
    user_id: UUID
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== MARKS SCHEMAS ====================

class StudentMarksBase(BaseModel):
    subject_name: str
    exam_type: str  # "assignment", "quiz", "midterm", "final"
    marks_obtained: float
    max_marks: float
    grade: Optional[str]

class StudentMarksCreate(StudentMarksBase):
    student_id: UUID
    academic_year_id: Optional[UUID]

class StudentMarksResponse(StudentMarksBase):
    id: UUID
    student_id: UUID
    academic_year_id: Optional[UUID]
    percentage: float
    recorded_date: datetime
    
    class Config:
        from_attributes = True

class ConsolidatedMarksResponse(BaseModel):
    student_id: UUID
    current_year: int
    overall_gpa: float
    marks_by_subject: List[StudentMarksResponse]

# ==================== DASHBOARD SCHEMAS ====================

class StudentDashboardResponse(BaseModel):
    student_info: StudentResponse
    progress: StudentProgressResponse
    current_year: int
    attendance: AttendanceSummaryResponse
    academic_content: ContentByYearResponse
    pending_assignments: List[StudentAssignmentResponse]
    pending_quizzes: List[StudentQuizResponse]
    recent_marks: List[StudentMarksResponse]
    notifications: List[NotificationResponse]
    todo_reminders: List[TodoReminderResponse]

class AdminDashboardResponse(BaseModel):
    total_students: int
    total_assignments: int
    total_quizzes: int
    pending_submissions: int
    average_attendance: float
    recent_logs: List[Any]  # Admin log entries

# ==================== ADMIN ACTION SCHEMAS ====================

class AdminLogResponse(BaseModel):
    id: UUID
    admin_id: UUID
    action: str
    entity_type: str
    entity_id: Optional[UUID]
    changes: dict
    timestamp: datetime
    
    class Config:
        from_attributes = True

# ==================== BATCH OPERATIONS SCHEMAS ====================

class BulkAttendanceUpdate(BaseModel):
    date: date
    attendance_records: List[AttendanceBase]

class BulkContentUpload(BaseModel):
    academic_year_id: UUID
    content_items: List[AcademicContentCreate]

class BulkMarksUpdate(BaseModel):
    marks_records: List[StudentMarksCreate]
