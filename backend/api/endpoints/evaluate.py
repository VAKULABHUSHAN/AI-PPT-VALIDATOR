import json
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from backend.core.database import get_db
from backend.schemas.evaluation import EvaluationResult, CategoryScore, SlideFeedback, JuryQuestion
from backend.rubrics.definitions import get_rubric_for_mode
from backend.schemas.rubric import RubricDefinition
from backend.ai.evaluator import evaluate_presentation
from backend.reports.generator import generate_pdf_report, generate_json_report
from backend.schemas.presentation import PresentationInfo, SlideContent
from backend.core.config import settings

router = APIRouter()

@router.get("/{presentation_id}")
async def get_evaluation(presentation_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM evaluations 
    WHERE presentation_id = ? 
    ORDER BY created_at DESC LIMIT 1
    """, (presentation_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Evaluation not found for this presentation")
        
    row_dict = dict(row)
    return {
        "id": row_dict["id"],
        "presentation_id": row_dict["presentation_id"],
        "mode": row_dict["mode"],
        "ai_mode_applied": row_dict.get("ai_mode_applied", "Offline heuristic evaluation"),
        "ai_model_name": row_dict.get("ai_model_name", ""),
        "overall_score": row_dict["overall_score"],
        "rating_label": row_dict["rating_label"],
        "verdict": row_dict["verdict"],
        "summary_text": row_dict["summary_text"],
        "category_scores": json.loads(row_dict["category_scores_json"]),
        "slide_feedback": json.loads(row_dict["slide_feedback_json"]),
        "critical_issues": json.loads(row_dict["critical_issues_json"]),
        "major_improvements": json.loads(row_dict["major_improvements_json"]),
        "minor_improvements": json.loads(row_dict["minor_improvements_json"]),
        "strengths": json.loads(row_dict["strengths_json"]),
        "jury_questions": json.loads(row_dict["jury_questions_json"]),
        "created_at": row_dict["created_at"]
    }

@router.post("/re-evaluate/{presentation_id}")
async def re_evaluate_presentation(presentation_id: str, mode: str, evaluation_mode_type: str = Query("hybrid")):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM presentations WHERE id = ?", (presentation_id,))
    pres_row = cursor.fetchone()
    
    if not pres_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Presentation not found")
        
    raw_slides = json.loads(pres_row["metadata_json"] or "[]")
    slides = [SlideContent(**s) for s in raw_slides]
    
    # Determine rubric
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
        
    evaluation = evaluate_presentation(presentation_id, slides, rubric, preferred_mode=evaluation_mode_type)
    
    # Save evaluation
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
    cursor.execute("UPDATE presentations SET mode = ? WHERE id = ?", (mode, presentation_id))
    conn.commit()
    conn.close()
    
    # Update reports
    pres_info = PresentationInfo(
        id=presentation_id,
        filename=pres_row["filename"],
        file_type=pres_row["file_type"],
        file_size_bytes=pres_row["file_size_bytes"],
        slide_count=pres_row["slide_count"],
        mode=mode,
        status="completed",
        progress_stage=7,
        progress_message="Evaluation completed.",
        created_at=pres_row["created_at"],
        updated_at=pres_row["updated_at"],
        slides=slides
    )
    pdf_path = settings.REPORTS_DIR / f"{presentation_id}.pdf"
    json_path = settings.REPORTS_DIR / f"{presentation_id}.json"
    generate_pdf_report(pres_info, evaluation, pdf_path)
    generate_json_report(evaluation, json_path)
    
    return evaluation
