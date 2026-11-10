import re
from pathlib import Path
from fastapi import UploadFile, HTTPException
from backend.core.config import settings

def validate_presentation_file(file: UploadFile) -> str:
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension '{ext}'. Only .pptx, .ppt, and .pdf are supported."
        )
    
    # Clean filename
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    return clean_name

