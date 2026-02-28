"""
Simplified database initialization - bypasses setup_db complexity
"""
import sys
import os

# Set PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 Initializing College Academic Portal Database...")

try:
    # Change to the Backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("✅ Working directory set to Backend")
    
    # Try importing and creating tables
    print("📚 Importing SQLAlchemy models...")
    from app.models import Base
    from app.database import engine
    
    print("🗂️  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    # Now seed some data
    print("\n🌱 Seeding test data...")
    from app.database import SessionLocal
    from app.models import User, Student, AcademicYear, AcademicContent
    from app.core.security import hash_password
    from datetime import datetime
    import uuid
    
    db = SessionLocal()
    
    # Create Academic Years
    print("  📚 Creating academic years...")
    for year in range(1, 5):
        existing = db.query(AcademicYear).filter(AcademicYear.year == year).first()
        if not existing:
            ay = AcademicYear(
                id=str(uuid.uuid4()),
                year=year,
                semester=1 if year % 2 == 1 else 2,
                department="CSE"
            )
            db.add(ay)
    db.commit()
    print("  ✅ Academic years created")
    
    # Create test student
    print("  👨‍🎓 Creating test student...")
    existing_user = db.query(User).filter(User.email == "john.doe@college.edu").first()
    if not existing_user:
        student_id = str(uuid.uuid4())
        user = User(
            id=student_id,
            email="john.doe@college.edu",
            password_hash=hash_password("TestPassword123!"),
            role="student"
        )
        db.add(user)
        db.flush()
        
        student = Student(
            id=str(uuid.uuid4()),
            user_id=student_id,
            name="John Doe",
            batch_year=2023,
            department="CSE"
        )
        db.add(student)
        db.commit()
        print("  ✅ Test student created")
    else:
        print("  ⚠️  Test student already exists")
    
    # Create test admin
    print("  👨‍💼 Creating test admin...")
    existing_admin = db.query(User).filter(User.email == "admin@college.edu").first()
    if not existing_admin:
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@college.edu",
            password_hash=hash_password("AdminPassword123!"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("  ✅ Test admin created")
    else:
        print("  ⚠️  Test admin already exists")
    
    db.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*60)
    print("\n📝 Test Credentials:")
    print("  Student:")
    print("    Email: john.doe@college.edu")
    print("    Password: TestPassword123!")
    print("\n  Admin:")
    print("    Email: admin@college.edu")
    print("    Password: AdminPassword123!")
    print("\n📝 Next steps:")
    print("   1. Ensure PostgreSQL is running with database: college_portal")
    print("   2. Start backend: python -m uvicorn app.main:app --reload")
    print("   3. Access API docs: http://localhost:8000/docs")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
