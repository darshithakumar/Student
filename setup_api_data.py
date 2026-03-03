#!/usr/bin/env python3
"""
Setup script to populate the backend with test data
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def print_result(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"[{title}]")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print('='*60)

# ==================== REGISTRATION ====================
print("\n" + "█"*60)
print("█ SETTING UP TEST DATA")
print("█"*60)

# Register Admin
print("\n1️⃣ Registering Admin User...")
admin_data = {
    "email": "admin@college.com",
    "password": "admin123",
    "name": "Admin User",
    "role": "admin"
}
r = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
print_result("Register Admin", r)
admin_id = r.json().get("user_id") if r.status_code == 200 else None

# Register Students
print("\n2️⃣ Registering Student Users...")
students = [
    {"email": "student1@college.com", "password": "pass123", "name": "John Doe", "batch_year": 2022, "department": "Computer Science"},
    {"email": "student2@college.com", "password": "pass123", "name": "Jane Smith", "batch_year": 2023, "department": "Electronics"},
    {"email": "student3@college.com", "password": "pass123", "name": "Bob Johnson", "batch_year": 2022, "department": "Computer Science"},
]

student_ids = []
for student in students:
    # Try the student-specific endpoint first
    r = requests.post(f"{BASE_URL}/auth/register/student", json=student)
    if r.status_code == 200:
        student_id = r.json().get("user_id")
        student_ids.append(student_id)
        print(f"✓ Registered {student['name']} ({student['email']})")
    else:
        print(f"✗ Failed to register {student['name']}: {r.text}")

print(f"Successfully registered {len(student_ids)} students")

# ==================== LOGIN & GET TOKEN ====================
print("\n3️⃣ Getting Auth Tokens...")
login_data = {"email": "admin@college.com", "password": "admin123"}
r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
if r.status_code == 200:
    admin_token = r.json().get("access_token")
    print(f"✓ Admin token obtained")
else:
    print(f"✗ Failed to get admin token: {r.text}")
    admin_token = None

headers_admin = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

# ==================== CREATE CONTENT ====================
print("\n4️⃣ Creating Course Content...")
content_data = {
    "title": "Data Structures",
    "description": "Learn fundamental data structures and algorithms",
    "subject": "Computer Science"
}
r = requests.post(f"{BASE_URL}/content", json=content_data, headers=headers_admin)
print_result("Create Content", r)
content_id = r.json().get("id") if r.status_code == 200 else None

# ==================== CREATE ASSIGNMENTS ====================
print("\n5️⃣ Creating Assignments...")
due_date = (datetime.now() + timedelta(days=7)).isoformat()
assignment_data = {
    "title": "Assignment 1 - Arrays",
    "description": "Implement basic array operations",
    "due_date": due_date,
    "content_id": content_id
}
r = requests.post(f"{BASE_URL}/assignments/create", json=assignment_data, headers=headers_admin)
print_result("Create Assignment", r)

# Create more assignments
assignments_list = [
    {"title": "Linked Lists", "description": "Implement singly and doubly linked lists"},
    {"title": "Stacks and Queues", "description": "Implementation and applications"},
    {"title": "Trees", "description": "Binary trees and traversal methods"},
]

for assignment in assignments_list:
    assignment["due_date"] = (datetime.now() + timedelta(days=14)).isoformat()
    assignment["content_id"] = content_id
    r = requests.post(f"{BASE_URL}/assignments/create", json=assignment, headers=headers_admin)
    if r.status_code == 200:
        print(f"✓ Created assignment: {assignment['title']}")
    else:
        print(f"✗ Failed to create: {assignment['title']}")

# ==================== CREATE QUIZZES ====================
print("\n6️⃣ Creating Quizzes...")
quiz_data = {
    "title": "Quiz 1 - Basics",
    "description": "Test your knowledge on data structure basics",
    "content_id": content_id,
    "total_marks": 10
}
r = requests.post(f"{BASE_URL}/quizzes/create", json=quiz_data, headers=headers_admin)
print_result("Create Quiz", r)

# ==================== MARK ATTENDANCE ====================
print("\n7️⃣ Marking Attendance...")
if student_ids:
    for student_id in student_ids:
        attendance_data = {
            "student_id": student_id,
            "date": datetime.now().date().isoformat(),
            "status": "present"
        }
        r = requests.post(f"{BASE_URL}/attendance/mark", json=attendance_data, headers=headers_admin)
        if r.status_code == 200:
            print(f"✓ Marked attendance for student {student_id}")
        else:
            print(f"✗ Failed to mark attendance: {r.text}")

# ==================== SUMMARY ====================
print("\n" + "█"*60)
print("█ SETUP COMPLETE")
print("█" + " "*58)
print(f"✓ Admin ID: {admin_id}")
print(f"✓ Student IDs: {', '.join(student_ids)}")
print(f"✓ Content ID: {content_id}")
print("█"*60)
print("\n🎉 Test data has been created!")
print(f"\n📝 Credentials for testing:")
print(f"   Admin:   admin@college.com / admin123")
print(f"   Student: student1@college.com / pass123")
print(f"   Student: student2@college.com / pass123")
print(f"   Student: student3@college.com / pass123")
print(f"\n🌐 Frontend: http://localhost:5173")
print(f"📚 API Docs: http://localhost:8000/docs")
