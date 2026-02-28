"""
Database initialization and setup script
This script:
1. Installs required dependencies
2. Creates PostgreSQL database if it doesn't exist
3. Creates all tables from models
4. Populates seed data for testing
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/college_portal")

def run_command(command, description):
    """Run a system command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"⚠️  Warning: {description}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {description}")
        print(f"Error details: {str(e)}")
        return False

def create_database():
    """Create PostgreSQL database if it doesn't exist"""
    print("\n🔄 Creating PostgreSQL database...")
    
    # Parse database URL
    # Format: postgresql://username:password@localhost:5432/database_name
    parts = DATABASE_URL.replace("postgresql://", "").split("@")
    creds = parts[0].split(":")
    user = creds[0]
    password = creds[1] if len(creds) > 1 else ""
    
    host_db = parts[1].split("/")
    host = host_db[0].split(":")[0]
    db_name = host_db[1]
    
    # Create database command
    if password:
        cmd = f'psql -U {user} -h {host} -tc "SELECT 1 FROM pg_database WHERE datname = \'{db_name}\'" | grep -q 1 || psql -U {user} -h {host} -c "CREATE DATABASE {db_name};"'
    else:
        cmd = f'psql -U {user} -h {host} -tc "SELECT 1 FROM pg_database WHERE datname = \'{db_name}\'" | grep -q 1 || psql -U {user} -h {host} -c "CREATE DATABASE {db_name};"'
    
    return run_command(cmd, "Create PostgreSQL database")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    return run_command(
        "pip install -r requirements.txt",
        "Install Python packages from requirements.txt"
    )

def create_tables():
    """Create database tables from SQLAlchemy models"""
    print("\n🗂️  Creating database tables...")
    print("Running init_db.py...")
    
    try:
        # Change to Backend directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Import and run
        from app.database import engine
        from app.models import Base
        
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

def seed_data():
    """Populate database with sample test data"""
    print("\n🌱 Seeding test data...")
    
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        from app.database import SessionLocal
        from app.models import User, Student, AcademicYear, AcademicContent, AdminLog
        from app.core.security import hash_password
        from datetime import datetime
        import uuid
        
        db = SessionLocal()
        
        # Create Academic Years (1-4)
        print("  📚 Creating academic years...")
        for year in range(1, 5):
            if not db.query(AcademicYear).filter(AcademicYear.year == year).first():
                academic_year = AcademicYear(
                    id=str(uuid.uuid4()),
                    year=year,
                    semester=1 if year % 2 == 1 else 2,
                    department="CSE"
                )
                db.add(academic_year)
        db.commit()
        
        # Create test students
        print("  👨‍🎓 Creating test students...")
        students_data = [
            {
                "email": "john.doe@college.edu",
                "name": "John Doe",
                "batch_year": 2023,
                "department": "CSE"
            },
            {
                "email": "jane.smith@college.edu",
                "name": "Jane Smith",
                "batch_year": 2023,
                "department": "CSE"
            },
            {
                "email": "alice.johnson@college.edu",
                "name": "Alice Johnson",
                "batch_year": 2022,
                "department": "ECE"
            },
            {
                "email": "bob.wilson@college.edu",
                "name": "Bob Wilson",
                "batch_year": 2022,
                "department": "ECE"
            }
        ]
        
        for student_data in students_data:
            if not db.query(User).filter(User.email == student_data["email"]).first():
                user_id = str(uuid.uuid4())
                
                # Create user
                user = User(
                    id=user_id,
                    email=student_data["email"],
                    password_hash=hash_password("TestPassword123!"),
                    role="student"
                )
                db.add(user)
                db.flush()
                
                # Create student
                student = Student(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    name=student_data["name"],
                    batch_year=student_data["batch_year"],
                    department=student_data["department"]
                )
                db.add(student)
        
        db.commit()
        
        # Create test admin
        print("  👨‍💼 Creating test admin...")
        if not db.query(User).filter(User.email == "admin@college.edu").first():
            admin = User(
                id=str(uuid.uuid4()),
                email="admin@college.edu",
                password_hash=hash_password("AdminPassword123!"),
                role="admin"
            )
            db.add(admin)
            db.commit()
        
        # Create sample content
        print("  📖 Creating sample content...")
        academic_years = db.query(AcademicYear).all()
        if academic_years:
            ay = academic_years[0]
            
            content_types = ["notes", "ppt", "textbook", "pyq", "demo_test"]
            subjects = ["Data Structures", "Algorithms", "Database Management", "Web Development"]
            
            for subject in subjects:
                for content_type in content_types:
                    content_id = str(uuid.uuid4())
                    content = AcademicContent(
                        id=content_id,
                        academic_year_id=ay.id,
                        subject_name=subject,
                        content_type=content_type,
                        title=f"{subject} - {content_type.upper()}",
                        description=f"Sample {content_type} for {subject}",
                        file_url=f"https://files.example.com/{subject.lower().replace(' ', '-')}-{content_type}.pdf",
                        version=1,
                        uploaded_at=datetime.utcnow()
                    )
                    db.add(content)
        
        db.commit()
        
        print("✅ Test data seeded successfully!")
        print("\n📝 Test Credentials:")
        print("  Student:")
        print("    Email: john.doe@college.edu")
        print("    Password: TestPassword123!")
        print("  Admin:")
        print("    Email: admin@college.edu")
        print("    Password: AdminPassword123!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error seeding data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("🚀 College Academic Portal - Database Setup")
    print("="*60)
    
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Create Tables", create_tables),
        ("Seed Test Data", seed_data),
    ]
    
    results = {}
    for step_name, step_func in steps:
        results[step_name] = step_func()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Setup Summary")
    print("="*60)
    
    for step_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {step_name}")
    
    if all(results.values()):
        print("\n🎉 Database setup completed successfully!")
        print("\n✅ Next steps:")
        print("   1. Start the backend: python -m uvicorn app.main:app --reload")
        print("   2. Open API docs: http://localhost:8000/docs")
        print("   3. Test with provided credentials")
    else:
        print("\n⚠️  Some steps failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
