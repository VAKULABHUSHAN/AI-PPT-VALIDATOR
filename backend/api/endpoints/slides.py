import json
from fastapi import APIRouter, HTTPException
from backend.core.database import get_db

router = APIRouter()

@router.get("/{presentation_id}")
async def get_presentation_slides(presentation_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM presentations WHERE id = ?", (presentation_id,))
    pres = cursor.fetchone()
    
    if not pres:
        conn.close()
        raise HTTPException(status_code=404, detail="Presentation not found")
        
    slides = json.loads(pres["metadata_json"] or "[]")
    
    # Also attach slide feedback if available
    cursor.execute("SELECT slide_feedback_json FROM evaluations WHERE presentation_id = ? ORDER BY created_at DESC LIMIT 1", (presentation_id,))
    eval_row = cursor.fetchone()
    conn.close()
    
    feedback_map = {}
    if eval_row and eval_row["slide_feedback_json"]:
        fb_list = json.loads(eval_row["slide_feedback_json"])
        for fb in fb_list:
            feedback_map[fb["slide_number"]] = fb
            
    enriched_slides = []
    for s in slides:
        s_num = s["slide_number"]
        fb = feedback_map.get(s_num, {})
        enriched_slides.append({
            **s,
            "feedback": fb
        })
        
    return {
        "presentation_id": presentation_id,
        "slide_count": pres["slide_count"],
        "slides": enriched_slides
    }

