import uuid
import json
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException

from backend.core.database import get_db
from backend.rubrics.definitions import BUILTIN_RUBRICS
from backend.schemas.rubric import RubricDefinition, CreateRubricRequest, Criterion

router = APIRouter()

@router.get("/")
async def list_rubrics():
    rubrics = list(BUILTIN_RUBRICS.values())
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rubrics ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    for r in rows:
        rubrics.append(RubricDefinition(
            id=r["id"],
            name=r["name"],
            description=r["description"],
            is_builtin=bool(r["is_builtin"]),
            mode_key=r["mode_key"],
            criteria=[Criterion(**c) for c in json.loads(r["criteria_json"])],
            mandatory_sections=json.loads(r["mandatory_sections_json"] or "[]"),
            min_passing_score=r["min_passing_score"],
            created_at=r["created_at"]
        ))
        
    return rubrics

@router.post("/")
async def create_custom_rubric(req: CreateRubricRequest):
    # Validate weightages sum to 100
    total_weight = sum([c.weightage for c in req.criteria])
    if abs(total_weight - 100.0) > 0.5:
        raise HTTPException(
            status_code=400,
            detail=f"Criteria weightages must sum to 100%. Current sum: {total_weight}%"
        )
        
    rubric_id = f"custom-{str(uuid.uuid4())[:8]}"
    mode_key = rubric_id
    now = datetime.now().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO rubrics (
        id, name, description, is_builtin, mode_key, criteria_json,
        mandatory_sections_json, min_passing_score, created_at
    ) VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?)
    """, (
        rubric_id,
        req.name,
        req.description,
        mode_key,
        json.dumps([c.model_dump() for c in req.criteria]),
        json.dumps(req.mandatory_sections),
        req.min_passing_score,
        now
    ))
    conn.commit()
    conn.close()
    
    return {
        "id": rubric_id,
        "name": req.name,
        "mode_key": mode_key,
        "message": "Custom rubric created successfully"
    }

@router.delete("/{rubric_id}")
async def delete_custom_rubric(rubric_id: str):
    if rubric_id in BUILTIN_RUBRICS or rubric_id.startswith("rubric-"):
        raise HTTPException(status_code=400, detail="Cannot delete built-in rubrics")
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rubrics WHERE id = ?", (rubric_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Rubric not found")
        
    return {"message": "Custom rubric deleted successfully"}

