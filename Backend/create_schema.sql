-- College Portal Database Schema
-- Auto-generated from SQLAlchemy models

-- ==================== USER & AUTH MODELS ====================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ==================== STUDENT MODELS ====================

CREATE TABLE IF NOT EXISTS students (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    name VARCHAR NOT NULL,
    batch_year INTEGER NOT NULL,
    department VARCHAR NOT NULL,
    current_year_override INTEGER,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_batch_department ON students(batch_year, department);

CREATE TABLE IF NOT EXISTS student_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(user_id),
    current_year INTEGER NOT NULL,
    gpa FLOAT DEFAULT 0.0,
    total_assignments_completed INTEGER DEFAULT 0,
    total_quizzes_attempted INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_student_progress_student_id ON student_progress(student_id);

-- ==================== ACADEMIC CONTENT MODELS ====================

CREATE TABLE IF NOT EXISTS academic_years (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    department VARCHAR NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_year_semester_dept ON academic_years(year, semester, department);

CREATE TABLE IF NOT EXISTS academic_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academic_year_id UUID NOT NULL REFERENCES academic_years(id),
    subject_name VARCHAR NOT NULL,
    content_type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    file_url VARCHAR NOT NULL,
    uploaded_by UUID REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_content_year_type ON academic_content(academic_year_id, content_type);

-- ==================== ATTENDANCE MODELS ====================

CREATE TABLE IF NOT EXISTS attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(user_id),
    date DATE NOT NULL,
    present BOOLEAN DEFAULT FALSE,
    marked_by UUID REFERENCES users(id),
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_id, date);

CREATE TABLE IF NOT EXISTS attendance_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(user_id),
    month INTEGER,
    year INTEGER,
    total_classes INTEGER DEFAULT 0,
    classes_attended INTEGER DEFAULT 0,
    attendance_percentage FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_attendance_summary_student_id ON attendance_summary(student_id);

-- ==================== ASSIGNMENT MODELS ====================

CREATE TABLE IF NOT EXISTS assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academic_year_id UUID NOT NULL REFERENCES academic_years(id),
    subject_name VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    instructions TEXT,
    file_url VARCHAR,
    created_by UUID NOT NULL REFERENCES users(id),
    due_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    max_marks INTEGER DEFAULT 10
);

CREATE TABLE IF NOT EXISTS student_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES assignments(id),
    student_id UUID NOT NULL REFERENCES students(user_id),
    submission_file_url VARCHAR,
    submission_date TIMESTAMP,
    status VARCHAR DEFAULT 'pending',
    marks_obtained FLOAT,
    feedback TEXT,
    graded_by UUID REFERENCES users(id),
    graded_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_student_assignment ON student_assignments(student_id, assignment_id);

-- ==================== QUIZ MODELS ====================

CREATE TABLE IF NOT EXISTS quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academic_year_id UUID NOT NULL REFERENCES academic_years(id),
    subject_name VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    max_marks INTEGER DEFAULT 10,
    duration_minutes INTEGER DEFAULT 30,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id),
    question_text TEXT NOT NULL,
    question_type VARCHAR,
    options JSONB,
    correct_answer VARCHAR,
    marks INTEGER DEFAULT 1,
    "order" INTEGER
);

CREATE TABLE IF NOT EXISTS student_quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id),
    student_id UUID NOT NULL REFERENCES students(user_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR DEFAULT 'in_progress',
    marks_obtained FLOAT,
    answers JSONB
);

CREATE INDEX IF NOT EXISTS idx_student_quiz ON student_quizzes(student_id, quiz_id);

-- ==================== NOTIFICATION MODELS ====================

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR,
    related_id UUID,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_recipient_id ON notifications(recipient_id);

-- ==================== TODO/TASKS MODELS ====================

CREATE TABLE IF NOT EXISTS todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(user_id),
    title VARCHAR NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_todos_student_id ON todos(student_id);

-- ==================== ANALYTICS/LOGS MODELS ====================

CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR NOT NULL,
    entity_type VARCHAR,
    entity_id UUID,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
