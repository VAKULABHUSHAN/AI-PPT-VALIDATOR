import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.core.config import settings

router = APIRouter()

@router.get("/{presentation_id}/pdf")
async def download_pdf_report(presentation_id: str):
    pdf_path = settings.REPORTS_DIR / f"{presentation_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF report not found. Please ensure evaluation is complete.")
    
    return FileResponse(
        path=str(pdf_path),
        filename=f"PPT_Validator_Report_{presentation_id[:8]}.pdf",
        media_type="application/pdf"
    )

@router.get("/{presentation_id}/json")
async def download_json_report(presentation_id: str):
    json_path = settings.REPORTS_DIR / f"{presentation_id}.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="JSON report not found. Please ensure evaluation is complete.")
        
    return FileResponse(
        path=str(json_path),
        filename=f"PPT_Validator_Report_{presentation_id[:8]}.json",
        media_type="application/json"
    )

