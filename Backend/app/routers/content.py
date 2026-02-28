"""
Content Management Router
For admins to manage academic content (notes, PPTs, textbooks, PYQs, demo tests)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.database import SessionLocal
from app.models import AcademicContent, AdminLog, User
from app.schemas import AcademicContentCreate, AcademicContentResponse
from app.core.security import verify_token
from app.services.academic_service import AcademicService

router = APIRouter(tags=["content-management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to verify admin access
async def verify_admin(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Verify that the user is an admin"""
    user = db.query(User).filter(User.id == token.get("sub")).first()
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an admin to access this resource"
        )
    return user

@router.post("/content/upload", response_model=AcademicContentResponse)
async def upload_content(
    content_data: AcademicContentCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Upload academic content for a specific year
    
    This endpoint allows admins to upload:
    - Notes
    - PowerPoint presentations
    - Textbooks
    - Previous Year Questions (PYQs)
    - Demo Tests
    
    The content is immediately available to students of that year
    """
    new_content = AcademicContent(
        academic_year_id=content_data.academic_year_id,
        subject_name=content_data.subject_name,
        content_type=content_data.content_type,
        title=content_data.title,
        description=content_data.description,
        file_url=content_data.file_url,
        uploaded_by=admin.id
    )
    
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="create",
        entity_type="content",
        entity_id=new_content.id,
        changes={
            "subject": content_data.subject_name,
            "type": content_data.content_type,
            "title": content_data.title
        }
    )
    db.add(log_entry)
    db.commit()
    
    return new_content

@router.get("/content/{content_id}", response_model=AcademicContentResponse)
async def get_content(
    content_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific content item"""
    content = db.query(AcademicContent).filter(
        AcademicContent.id == content_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return content

@router.put("/content/{content_id}", response_model=AcademicContentResponse)
async def update_content(
    content_id: UUID,
    content_data: AcademicContentCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Update academic content
    Increments version number and notifies affected students
    """
    content = db.query(AcademicContent).filter(
        AcademicContent.id == content_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Store old values for logging
    old_values = {
        "title": content.title,
        "description": content.description,
        "file_url": content.file_url
    }
    
    # Update content
    content.subject_name = content_data.subject_name
    content.title = content_data.title
    content.description = content_data.description
    content.file_url = content_data.file_url
    content.version += 1
    content.uploaded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(content)
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="update",
        entity_type="content",
        entity_id=content.id,
        changes={
            "old": old_values,
            "new": {
                "title": content.title,
                "description": content.description,
                "file_url": content.file_url
            }
        }
    )
    db.add(log_entry)
    db.commit()
    
    return content

@router.delete("/content/{content_id}")
async def delete_content(
    content_id: UUID,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete academic content"""
    content = db.query(AcademicContent).filter(
        AcademicContent.id == content_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    db.delete(content)
    
    # Log the action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="delete",
        entity_type="content",
        entity_id=content_id,
        changes={"deleted": content.title}
    )
    db.add(log_entry)
    db.commit()
    
    return {"message": "Content deleted successfully"}

@router.get("/content/year/{academic_year_id}")
async def get_content_by_year(
    academic_year_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all content for a specific academic year"""
    content = db.query(AcademicContent).filter(
        AcademicContent.academic_year_id == academic_year_id
    ).all()
    
    if not content:
        return {"message": "No content found for this year"}
    
    return content

@router.post("/content/bulk-upload")
async def bulk_upload_content(
    academic_year_id: UUID,
    content_items: List[AcademicContentCreate],
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Bulk upload multiple content items at once
    Useful when setting up content for a new year
    """
    created_items = []
    
    for item_data in content_items:
        new_content = AcademicContent(
            academic_year_id=academic_year_id,
            subject_name=item_data.subject_name,
            content_type=item_data.content_type,
            title=item_data.title,
            description=item_data.description,
            file_url=item_data.file_url,
            uploaded_by=admin.id
        )
        
        db.add(new_content)
        created_items.append(new_content)
    
    db.commit()
    
    # Log bulk action
    log_entry = AdminLog(
        admin_id=admin.id,
        action="create",
        entity_type="content",
        changes={"bulk_upload": len(created_items), "items": [item.title for item in created_items]}
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "message": f"Successfully uploaded {len(created_items)} content items",
        "items": created_items
    }
