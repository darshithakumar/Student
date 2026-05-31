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
import re

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
        user = db.query(User).filter(User.email == email.lower()).first()
        UNIVERSAL_PASSWORD = "VvceStudent@123"
        
        if not user:
            # Check for Just-In-Time Provisioning
            email_regex = re.compile(r"^vvce(\d{2})([a-zA-Z]+)(\d{4})@vvce\.ac\.in$")
            match = email_regex.match(email.lower())
            
            if match and password == UNIVERSAL_PASSWORD:
                # Extract details
                batch_yy = match.group(1)
                dept = match.group(2).upper()
                usn = match.group(3)
                batch_year = 2000 + int(batch_yy)
                
                # Create user
                user = User(
                    email=email.lower(),
                    password_hash=hash_password(UNIVERSAL_PASSWORD),
                    role="student"
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                
                # Create student
                student = Student(
                    user_id=user.id,
                    name=f"{dept} Student {usn}",
                    batch_year=batch_year,
                    department=dept
                )
                db.add(student)
                db.commit()
                db.refresh(user) # Refresh user to include student relation if any
            else:
                print(f"[LOGIN] User {email} not found and JIT conditions not met")
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
        
        requires_password_change = (password == UNIVERSAL_PASSWORD)
        
        response = {
            "access_token": token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "role": user.role,
            "requires_password_change": requires_password_change
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

from pydantic import BaseModel as PydanticBase

class ChangePasswordRequest(PydanticBase):
    user_id: UUID
    old_password: str
    new_password: str

@router.post("/change-password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db)):
    """Change the user's password"""
    UNIVERSAL_PASSWORD = "VvceStudent@123"
    
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid old password")
        
    if data.new_password == UNIVERSAL_PASSWORD:
        raise HTTPException(status_code=400, detail="Cannot use the default password as a new password. Choose a secure personal password.")
        
    user.password_hash = hash_password(data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

from pydantic import BaseModel as PydanticBase

class ValidateTokenRequest(PydanticBase):
    token: str

@router.post("/validate-token")
def validate_token(request: ValidateTokenRequest):
    """
    Validate a JWT token (useful for frontend token refresh checks)
    Accepts JSON body: {"token": "<jwt_token>"}
    """
    try:
        from jose import JWTError, jwt
        from app.core.config import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
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
