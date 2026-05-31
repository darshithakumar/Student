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

import re

@router.post("/login", response_model=dict)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    """
    Login and get JWT token - with error handling
    """
    try:
        email = data.email.lower().strip()
        password = data.password
        
        UNIVERSAL_DEFAULT_PASSWORD = "VvceStudent@123"
        
        print(f"[LOGIN] Attempting login for: {email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        print(f"[LOGIN] User found: {user is not None}")
        
        # JIT Provisioning Logic
        if not user:
            if password == UNIVERSAL_DEFAULT_PASSWORD:
                # Validate vvce domain and extract info
                match = re.match(r"^vvce(\d{2})([a-z]+)(\d{4})@vvce\.ac\.in$", email)
                if match:
                    batch_year_short = match.group(1)
                    branch = match.group(2).upper()
                    
                    batch_year = 2000 + int(batch_year_short)
                    
                    # Create User
                    user = User(
                        email=email,
                        password_hash=hash_password(password),
                        role="student"
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    
                    # Create Student
                    student = Student(
                        user_id=user.id,
                        name=f"Student {branch}-{batch_year_short}",
                        batch_year=batch_year,
                        department=branch
                    )
                    db.add(student)
                    db.commit()
                    db.refresh(student)
                    print(f"[LOGIN] JIT Provisioned student: {email}")
                else:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email format or password")
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        print(f"[LOGIN] Verifying password for {email}")
        # Verify password
        is_valid = verify_password(password, user.password_hash)
        print(f"[LOGIN] Password valid: {is_valid}")
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
            
        requires_password_change = verify_password(UNIVERSAL_DEFAULT_PASSWORD, user.password_hash)
        
        print(f"[LOGIN] Creating token for user {user.id}")
        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "requires_password_change": requires_password_change
        }
        print(f"[LOGIN] Token data: {token_data}")
        
        token = create_token(token_data)
        print(f"[LOGIN] Token created successfully")
        
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

 c l a s s   C h a n g e P a s s w o r d R e q u e s t ( P y d a n t i c B a s e ) : 
         t o k e n :   s t r 
         n e w _ p a s s w o r d :   s t r 
 
 @ r o u t e r . p o s t ( " / c h a n g e - p a s s w o r d " ) 
 d e f   c h a n g e _ p a s s w o r d ( r e q u e s t :   C h a n g e P a s s w o r d R e q u e s t ,   d b :   S e s s i o n   =   D e p e n d s ( g e t _ d b ) ) : 
         " " " 
         C h a n g e   t h e   u s e r   p a s s w o r d   a f t e r   i n i t i a l   J I T   l o g i n 
         " " " 
         t r y : 
                 f r o m   j o s e   i m p o r t   J W T E r r o r ,   j w t 
                 f r o m   a p p . c o r e . c o n f i g   i m p o r t   S E C R E T _ K E Y ,   A L G O R I T H M 
                 
                 p a y l o a d   =   j w t . d e c o d e ( r e q u e s t . t o k e n ,   S E C R E T _ K E Y ,   a l g o r i t h m s = [ A L G O R I T H M ] ) 
                 u s e r _ i d   =   p a y l o a d . g e t ( " s u b " ) 
                 
                 i f   n o t   u s e r _ i d : 
                         r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 1 ,   d e t a i l = " I n v a l i d   t o k e n " ) 
                         
                 u s e r   =   d b . q u e r y ( U s e r ) . f i l t e r ( U s e r . i d   = =   u s e r _ i d ) . f i r s t ( ) 
                 i f   n o t   u s e r : 
                         r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 4 ,   d e t a i l = " U s e r   n o t   f o u n d " ) 
                         
                 u s e r . p a s s w o r d _ h a s h   =   h a s h _ p a s s w o r d ( r e q u e s t . n e w _ p a s s w o r d ) 
                 d b . c o m m i t ( ) 
                 
                 r e t u r n   { " m e s s a g e " :   " P a s s w o r d   c h a n g e d   s u c c e s s f u l l y " } 
         e x c e p t   E x c e p t i o n   a s   e : 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 0 ,   d e t a i l = " I n v a l i d   t o k e n   o r   r e q u e s t " ) 
  
 