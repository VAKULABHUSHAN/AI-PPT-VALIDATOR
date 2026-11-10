import os
import uuid
import json
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks

from backend.core.config import settings
from backend.core.database import get_db
from backend.processors.file_validator import validate_presentation_file
from backend.processors.pptx_extractor import extract_pptx_content
from backend.processors.pdf_extractor import extract_pdf_content
from backend.processors.slide_renderer import render_presentation_slides
from backend.rubrics.definitions import get_rubric_for_mode, BUILTIN_RUBRICS
from backend.schemas.rubric import RubricDefinition
from backend.ai.evaluator import evaluate_presentation
from backend.reports.generator import generate_pdf_report, generate_json_report
from backend.schemas.presentation import SlideContent, PresentationInfo

router = APIRouter()

def process_presentation_pipeline(presentation_id: str, file_path: Path, ext: str, mode: str, evaluation_mode_type: str = "hybrid"):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Stage 2: Extracting slide content
        cursor.execute("UPDATE presentations SET progress_stage = 2, progress_message = 'Extracting slide content...' WHERE id = ?", (presentation_id,))
        conn.commit()
        
        slides: list[SlideContent] = []
        if ext in [".pptx", ".ppt"]:
            slides = extract_pptx_content(file_path)
        elif ext == ".pdf":
            slides = extract_pdf_content(file_path)
            
        slide_count = len(slides)
        
        # Stage 3: Rendering slides
        cursor.execute("UPDATE presentations SET progress_stage = 3, progress_message = 'Rendering slides for visual inspection...', slide_count = ? WHERE id = ?", (slide_count, presentation_id))
        conn.commit()
        
        slides_out_dir = settings.SLIDES_DIR / presentation_id
        render_presentation_slides(file_path, ext, slides, slides_out_dir)
            
        # Update preview URLs in slides
        for s in slides:
            s.preview_image_url = f"/static/slides/{presentation_id}/slide_{s.slide_number}.png"
            
        # Stage 4: Analyzing structure
        cursor.execute("UPDATE presentations SET progress_stage = 4, progress_message = 'Analyzing structure and presentation flow...' WHERE id = ?", (presentation_id,))
        conn.commit()
        
        # Determine rubric: check custom rubrics first, then builtin
        rubric: RubricDefinition = get_rubric_for_mode(mode)
        cursor.execute("SELECT * FROM rubrics WHERE id = ? OR mode_key = ?", (mode, mode))
        custom_row = cursor.fetchone()
        if custom_row:
            rubric = RubricDefinition(
                id=custom_row["id"],
                name=custom_row["name"],
                description=custom_row["description"],
                is_builtin=bool(custom_row["is_builtin"]),
                mode_key=custom_row["mode_key"],
                criteria=json.loads(custom_row["criteria_json"]),
                mandatory_sections=json.loads(custom_row["mandatory_sections_json"]),
                min_passing_score=custom_row["min_passing_score"]
            )
            
        # Stage 5: Evaluating technical depth & consistency
        cursor.execute("UPDATE presentations SET progress_stage = 5, progress_message = 'Evaluating technical depth, architecture, and credibility...' WHERE id = ?", (presentation_id,))
        conn.commit()
        
        # Stage 6: Evaluating visual quality & design readability
        cursor.execute("UPDATE presentations SET progress_stage = 6, progress_message = 'Evaluating visual quality, layout balance, and readability...' WHERE id = ?", (presentation_id,))
        conn.commit()
        
        # Run AI Evaluator
        evaluation = evaluate_presentation(presentation_id, slides, rubric, preferred_mode=evaluation_mode_type)
        
        # Stage 7: Generating report
        cursor.execute("UPDATE presentations SET progress_stage = 7, progress_message = 'Synthesizing explainable scorecard & reports...' WHERE id = ?", (presentation_id,))
        conn.commit()
        
        # Save evaluation to DB
        cursor.execute("""
        INSERT INTO evaluations (
            id, presentation_id, mode, ai_mode_applied, ai_model_name,
            overall_score, rating_label, verdict, summary_text,
            category_scores_json, slide_feedback_json, critical_issues_json,
            major_improvements_json, minor_improvements_json, strengths_json,
            jury_questions_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evaluation.id,
            presentation_id,
            mode,
            evaluation.ai_mode_applied,
            evaluation.ai_model_name or "",
            evaluation.overall_score,
            evaluation.rating_label,
            evaluation.verdict,
            evaluation.summary_text,
            json.dumps([c.model_dump() for c in evaluation.category_scores]),
            json.dumps([s.model_dump() for s in evaluation.slide_feedback]),
            json.dumps(evaluation.critical_issues),
            json.dumps(evaluation.major_improvements),
            json.dumps(evaluation.minor_improvements),
            json.dumps(evaluation.strengths),
            json.dumps([jq.model_dump() for jq in evaluation.jury_questions]),
            evaluation.created_at
        ))
        
        # Generate PDF and JSON reports
        pres_info = PresentationInfo(
            id=presentation_id,
            filename=file_path.name,
            file_type=ext,
            file_size_bytes=os.path.getsize(file_path),
            slide_count=slide_count,
            mode=mode,
            status="completed",
            progress_stage=7,
            progress_message="Evaluation completed.",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            slides=slides
        )
        pdf_path = settings.REPORTS_DIR / f"{presentation_id}.pdf"
        json_path = settings.REPORTS_DIR / f"{presentation_id}.json"
        generate_pdf_report(pres_info, evaluation, pdf_path)
        generate_json_report(evaluation, json_path)
        
        # Update presentation record as completed
        cursor.execute("""
        UPDATE presentations SET 
            status = 'completed',
            progress_stage = 7,
            progress_message = 'Evaluation complete',
            slide_count = ?,
            metadata_json = ?,
            updated_at = ?
        WHERE id = ?
        """, (
            slide_count,
            json.dumps([s.model_dump() for s in slides]),
            datetime.now().isoformat(),
            presentation_id
        ))
        conn.commit()
        
    except Exception as e:
        cursor.execute("""
        UPDATE presentations SET 
            status = 'failed',
            error_message = ?,
            progress_message = 'Processing failed',
            updated_at = ?
        WHERE id = ?
        """, (str(e), datetime.now().isoformat(), presentation_id))
        conn.commit()
    finally:
        conn.close()

@router.post("/upload")
async def upload_presentation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("sih"),
    evaluation_mode_type: str = Form("hybrid")
):
    safe_name = validate_presentation_file(file)
    ext = Path(safe_name).suffix.lower()
    
    presentation_id = str(uuid.uuid4())
    save_filename = f"{presentation_id}_{safe_name}"
    save_path = settings.UPLOADS_DIR / save_filename
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(save_path)
    now = datetime.now().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO presentations (
        id, filename, file_path, file_type, file_size_bytes, slide_count,
        mode, status, progress_stage, progress_message, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        presentation_id, safe_name, str(save_path), ext, file_size, 0,
        mode, "processing", 1, "Uploading presentation...", now, now
    ))
    conn.commit()
    conn.close()
    
    # Run processing pipeline via background task
    background_tasks.add_task(process_presentation_pipeline, presentation_id, save_path, ext, mode, evaluation_mode_type)
    
    return {
        "presentation_id": presentation_id,
        "filename": safe_name,
        "mode": mode,
        "status": "processing",
        "progress_stage": 1,
        "message": "Presentation uploaded successfully. Evaluation underway."
    }

@router.get("/status/{presentation_id}")
async def get_processing_status(presentation_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM presentations WHERE id = ?", (presentation_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Presentation not found")
        
    return {
        "presentation_id": row["id"],
        "filename": row["filename"],
        "status": row["status"],
        "progress_stage": row["progress_stage"],
        "progress_message": row["progress_message"],
        "error_message": row["error_message"],
        "slide_count": row["slide_count"],
        "mode": row["mode"]
    }

