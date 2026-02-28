#!/usr/bin/env python3
"""
Create test data for the College Portal
Run this after database is created to populate with test users and content
"""

import sys
from datetime import datetime, timedelta
sys.path.insert(0, 'D:\\Clg')

from app.database import SessionLocal, engine
from app.models import (
    Base, User, Student, StudentProgress, AcademicYear, AcademicContent,
    Assignment, StudentAssignment, Quiz, QuizQuestion, StudentQuiz,
    Attendance, AttendanceSummary, StudentMarks, Notification, TodoReminder, AdminLog
)

# Simple password hashing (MD5 for testing only - NOT for production)
import hashlib

def simple_hash(password):
    return hashlib.md5(password.encode()).hexdigest()

def create_test_data():
    """Create test students, admin, assignments, quizzes, and content"""
    db = SessionLocal()
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created/verified")
        
        # Clear existing test data
        db.query(TodoReminder).delete()
        db.query(AdminLog).delete()
        db.query(Notification).delete()
        db.query(StudentMarks).delete()
        db.query(AttendanceSummary).delete()
        db.query(Attendance).delete()
        db.query(AcademicContent).delete()
        db.query(StudentQuiz).delete()
        db.query(QuizQuestion).delete()
        db.query(Quiz).delete()
        db.query(StudentAssignment).delete()
        db.query(Assignment).delete()
        db.query(StudentProgress).delete()
        db.query(Student).delete()
        db.query(AcademicYear).delete()
        db.query(User).delete()
        db.commit()
        print("✅ Cleared existing test data")
        
        # Create Academic Years (for current academic year 2025-26)
        academic_years = []
        for year in range(1, 5):
            ay = AcademicYear(
                year=year,
                semester=1,
                department="CSE",
                start_date=datetime(2025, 8, 15),
                end_date=datetime(2025, 12, 31)
            )
            db.add(ay)
            academic_years.append(ay)
        
        ay_ece = AcademicYear(
            year=3,
            semester=1,
            department="ECE",
            start_date=datetime(2025, 8, 15),
            end_date=datetime(2025, 12, 31)
        )
        db.add(ay_ece)
        academic_years.append(ay_ece)
        
        db.commit()
        print("✅ Created academic years")
        
        # Create Admin User
        admin_user = User(
            email="admin@college.com",
            password_hash=simple_hash("admin123"),
            role="admin"
        )
        db.add(admin_user)
        db.flush()
        print("✅ Created admin user (admin@college.com / admin123)")
        
        # Create Test Students (different batch years for year-based content)
        students_data = [
            {
                "email": "student1@college.com",
                "password": "student123",
                "name": "Raj Kumar",
                "batch_year": 2024,  # 1st year
                "department": "CSE"
            },
            {
                "email": "student2@college.com",
                "password": "student123",
                "name": "Priya Singh",
                "batch_year": 2023,  # 2nd year
                "department": "CSE"
            },
            {
                "email": "student3@college.com",
                "password": "student123",
                "name": "Arjun Patel",
                "batch_year": 2022,  # 3rd year
                "department": "ECE"
            },
            {
                "email": "student4@college.com",
                "password": "student123",
                "name": "Neha Sharma",
                "batch_year": 2021,  # 4th year
                "department": "ECE"
            }
        ]
        
        students = []
        for student_data in students_data:
            user = User(
                email=student_data["email"],
                password_hash=simple_hash(student_data["password"]),
                role="student"
            )
            db.add(user)
            db.flush()
            
            student = Student(
                user_id=user.id,
                name=student_data["name"],
                batch_year=student_data["batch_year"],
                department=student_data["department"]
            )
            db.add(student)
            db.flush()
            
            # Create student progress
            current_year = 2026 - student_data["batch_year"] + 1
            progress = StudentProgress(
                student_id=user.id,
                current_year=current_year,
                gpa=3.5 + (0.2 * len(students)),
                total_assignments_completed=5,
                total_quizzes_attempted=3
            )
            db.add(progress)
            students.append(student)
        
        db.commit()
        print(f"✅ Created {len(students)} test students")
        
        # Create Content for each year
        content_data = [
            # 1st Year Content
            {
                "year": 1,
                "subject_name": "Data Structures",
                "content_type": "notes",
                "title": "Arrays and Linked Lists - Complete Notes",
                "file_url": "https://drive.google.com/file/d/1example1"
            },
            {
                "year": 1,
                "subject_name": "Data Structures",
                "content_type": "ppt",
                "title": "Arrays Presentation - Lecture 1",
                "file_url": "https://drive.google.com/file/d/1example2"
            },
            {
                "year": 1,
                "subject_name": "Web Development",
                "content_type": "notes",
                "title": "HTML & CSS Fundamentals",
                "file_url": "https://drive.google.com/file/d/1example3"
            },
            {
                "year": 1,
                "subject_name": "Web Development",
                "content_type": "demo_test",
                "title": "Basic HTML Practice Test",
                "file_url": "https://drive.google.com/file/d/1example4"
            },
            # 2nd Year Content
            {
                "year": 2,
                "subject_name": "Database Management",
                "content_type": "notes",
                "title": "SQL Queries and Optimization",
                "file_url": "https://drive.google.com/file/d/1example5"
            },
            {
                "year": 2,
                "subject_name": "Database Management",
                "content_type": "textbook",
                "title": "Database System Concepts - Chen",
                "file_url": "https://drive.google.com/file/d/1example6"
            },
            {
                "year": 2,
                "subject_name": "Software Engineering",
                "content_type": "ppt",
                "title": "SDLC Models and Methodologies",
                "file_url": "https://drive.google.com/file/d/1example7"
            },
            # 3rd Year Content
            {
                "year": 3,
                "subject_name": "Machine Learning",
                "content_type": "notes",
                "title": "Supervised Learning Algorithms",
                "file_url": "https://drive.google.com/file/d/1example8"
            },
            {
                "year": 3,
                "subject_name": "Machine Learning",
                "content_type": "pyq",
                "title": "Previous Year ML Interview Questions",
                "file_url": "https://drive.google.com/file/d/1example9"
            },
            {
                "year": 3,
                "subject_name": "Cloud Computing",
                "content_type": "textbook",
                "title": "AWS Certified Solutions Architect",
                "file_url": "https://drive.google.com/file/d/1example10"
            },
            # 4th Year Content
            {
                "year": 4,
                "subject_name": "Project Management",
                "content_type": "notes",
                "title": "Agile & Scrum Methodologies",
                "file_url": "https://drive.google.com/file/d/1example11"
            },
            {
                "year": 4,
                "subject_name": "Capstone Project",
                "content_type": "ppt",
                "title": "Project Presentation Guidelines",
                "file_url": "https://drive.google.com/file/d/1example12"
            }
        ]
        
        for content in content_data:
            year = content.pop("year")
            ay = [a for a in academic_years if a.year == year and a.department == "CSE"]
            if ay:
                new_content = AcademicContent(
                    academic_year_id=ay[0].id,
                    uploaded_by=admin_user.id,
                    **content
                )
                db.add(new_content)
        
        db.commit()
        print(f"✅ Created {len(content_data)} study materials")
        
        # Create Assignments
        assignment_data = [
            {
                "academic_year_id": academic_years[0].id,
                "title": "Array Implementation Assignment",
                "description": "Implement basic array operations (insert, delete, search)",
                "subject_name": "Data Structures",
                "due_date": datetime.now() + timedelta(days=5),
                "max_marks": 10,
                "created_by": admin_user.id
            },
            {
                "academic_year_id": academic_years[0].id,
                "title": "Linked List Problems",
                "description": "Solve 10 linked list problems from LeetCode",
                "subject_name": "Data Structures",
                "due_date": datetime.now() + timedelta(days=7),
                "max_marks": 15,
                "created_by": admin_user.id
            },
            {
                "academic_year_id": academic_years[0].id,
                "title": "Create Personal Portfolio Website",
                "description": "Build a responsive portfolio using HTML, CSS, JavaScript",
                "subject_name": "Web Development",
                "due_date": datetime.now() + timedelta(days=10),
                "max_marks": 20,
                "created_by": admin_user.id
            },
            {
                "academic_year_id": academic_years[1].id,
                "title": "Database Normalization",
                "description": "Design normalized database schemas for given requirements",
                "subject_name": "Database Management",
                "due_date": datetime.now() + timedelta(days=8),
                "max_marks": 10,
                "created_by": admin_user.id
            }
        ]
        
        assignments = []
        for assignment in assignment_data:
            new_assignment = Assignment(**assignment)
            db.add(new_assignment)
            assignments.append(new_assignment)
        
        db.commit()
        print(f"✅ Created {len(assignments)} assignments")
        
        # Create Quizzes
        quiz_data = [
            {
                "academic_year_id": academic_years[0].id,
                "title": "Data Structures Basics Quiz",
                "description": "Test your knowledge on arrays, lists, stacks, and queues",
                "subject_name": "Data Structures",
                "duration_minutes": 30,
                "max_marks": 10,
                "created_by": admin_user.id
            },
            {
                "academic_year_id": academic_years[0].id,
                "title": "CSS Styling Challenge",
                "description": "Quick quiz on CSS properties and selectors",
                "subject_name": "Web Development",
                "duration_minutes": 20,
                "max_marks": 5,
                "created_by": admin_user.id
            },
            {
                "academic_year_id": academic_years[1].id,
                "title": "SQL Query Optimization",
                "description": "Optimize SQL queries for performance",
                "subject_name": "Database Management",
                "duration_minutes": 45,
                "max_marks": 15,
                "created_by": admin_user.id
            },
            {
                "academic_year_id": academic_years[2].id,
                "title": "Machine Learning Concepts",
                "description": "Advanced ML algorithms and their applications",
                "subject_name": "Machine Learning",
                "duration_minutes": 60,
                "max_marks": 20,
                "created_by": admin_user.id
            }
        ]
        
        quizzes = []
        for quiz in quiz_data:
            new_quiz = Quiz(**quiz)
            db.add(new_quiz)
            quizzes.append(new_quiz)
        
        db.commit()
        print(f"✅ Created {len(quizzes)} quizzes")
        
        # Add attendance records
        today = datetime.now().date()
        for i, student in enumerate(students):
            for days_back in range(30):
                attendance_date = today - timedelta(days=days_back)
                # Mark 80% of days as present
                is_present = ((attendance_date.weekday() < 5) and (days_back % 5 != 0))
                
                attendance = Attendance(
                    student_id=student.user_id,
                    date=attendance_date,
                    present=is_present,
                    marked_by=admin_user.id
                )
                db.add(attendance)
        
        db.commit()
        print("✅ Created attendance records")
        
        # Add notifications
        for i, student in enumerate(students):
            notification = Notification(
                recipient_id=student.user_id,
                title=f"Welcome to College Portal",
                message=f"Hi {student.name}, your dashboard is ready. Check your materials and assignments!",
                notification_type="info",
                is_read=False
            )
            db.add(notification)
        
        db.commit()
        print("✅ Created notifications")
        
        # Add todos/reminders
        for i, student in enumerate(students):
            for j in range(3):
                todo = TodoReminder(
                    user_id=student.user_id,
                    task_title=f"Complete Assignment {j+1}",
                    description=f"Work on assignment {j+1}",
                    due_date=datetime.now() + timedelta(days=5+j),
                    priority="medium",
                    category="assignment",
                    is_completed=False
                )
                db.add(todo)
        
        db.commit()
        print("✅ Created todos/reminders")
        
        print("\n" + "="*50)
        print("✅ TEST DATA CREATED SUCCESSFULLY!")
        print("="*50)
        print("\n📝 Test Credentials:\n")
        print("ADMIN:")
        print("  Email: admin@college.com")
        print("  Password: admin123\n")
        print("STUDENTS:")
        for i, student_data in enumerate(students_data, 1):
            batch_to_year = 2026 - student_data["batch_year"] + 1
            print(f"  Student {i}: {student_data['email']}")
            print(f"    Password: student123")
            print(f"    Name: {student_data['name']}")
            print(f"    Batch: {student_data['batch_year']} ({batch_to_year} year)")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
