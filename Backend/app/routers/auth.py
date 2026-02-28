"""
Authentication Router
User registration, login, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import SessionLocal
from app.models import User, Student
from app.schemas import RegisterSchema, LoginSchema, TokenSchema, StudentCreate
from app.core.security import hash_password, verify_password, create_token

router = APIRouter(tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=dict)
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    """
    Register a new user
    
    For students, batch_year is required and will be used for auto year calculation
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # If role is student, also need to create student record
    if data.role == "student":
        # This should ideally be called with additional fields
        # For now, you'll need to complete student profile separately
        pass
    
    return {
        "message": "User registered successfully",
        "user_id": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role
    }

@router.post("/register/student", response_model=dict)
def register_student(
    email: str,
    password: str,
    name: str,
    batch_year: int,
    department: str,
    db: Session = Depends(get_db)
):
    """
    Register a new student with full profile
    
    batch_year: Year the student joined (e.g., 2020, 2021, 2022, etc.)
    This is the KEY value used for automatic year calculation!
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    new_user = User(
        email=email,
        password_hash=hash_password(password),
        role="student"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create student record
    student = Student(
        user_id=new_user.id,
        name=name,
        batch_year=batch_year,
        department=department
    )
    
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return {
        "message": "Student registered successfully",
        "user_id": str(new_user.id),
        "student_id": str(student.user_id),
        "email": new_user.email,
        "name": name,
        "batch_year": batch_year,
        "department": department
    }

@router.post("/login", response_model=dict)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    """
    Login and get JWT token - with error handling
    """
    try:
        email = data.email
        password = data.password
        
        print(f"[LOGIN] Attempting login for: {email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        print(f"[LOGIN] User found: {user is not None}")
        
        if not user:
            print(f"[LOGIN] User {email} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        print(f"[LOGIN] Verifying password for {email}")
        # Verify password
        is_valid = verify_password(password, user.password_hash)
        print(f"[LOGIN] Password valid: {is_valid}")
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        print(f"[LOGIN] Creating token for user {user.id}")
        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
        print(f"[LOGIN] Token data: {token_data}")
        
        token = create_token(token_data)
        print(f"[LOGIN] Token created successfully")
        
        response = {
            "access_token": token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "role": user.role
        }
        
        print(f"[LOGIN] Login successful for {email}")
        return response
        
    except HTTPException as he:
        print(f"[LOGIN] HTTPException: {he.detail}")
        raise
    except Exception as e:
        import traceback
        print(f"[LOGIN] Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@router.post("/validate-token")
def validate_token(token: str):
    """
    Validate a JWT token (useful for frontend token refresh checks)
    """
    try:
        from app.core.security import verify_token
        from jose import JWTError, jwt
        from app.core.config import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {
            "valid": True,
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
