import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, Media
from app.schemas.schemas import MediaResponse
from app.core.auth import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/media/upload", response_model=MediaResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a media file"""
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Save media record to database
    media = Media(
        uploader_id=current_user.user_id,
        file_path=unique_filename,  # Store relative path
        encrypted_metadata=""  # Will be populated in Phase 3
    )
    
    db.add(media)
    db.commit()
    db.refresh(media)
    
    return media


@router.get("/media/{media_id}", response_model=MediaResponse)
def get_media_info(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get media file information"""
    media = db.query(Media).filter(Media.media_id == media_id).first()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    return media