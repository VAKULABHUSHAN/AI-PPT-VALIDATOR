import json
from fastapi import APIRouter
from backend.core.database import get_db

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics():
    conn = get_db()
    cursor = conn.cursor()
    
    # Total presentations
    cursor.execute("SELECT COUNT(*) as count FROM presentations")
    total_count = cursor.fetchone()["count"]
    
    # Average score
    cursor.execute("SELECT AVG(overall_score) as avg_score FROM evaluations")
    avg_score_res = cursor.fetchone()["avg_score"]
    avg_score = round(avg_score_res, 1) if avg_score_res is not None else 0.0
    
    # Recent evaluations with presentation details
    cursor.execute("""
    SELECT 
        e.id as eval_id,
        e.presentation_id,
        e.mode,
        e.overall_score,
        e.rating_label,
        e.verdict,
        e.created_at,
        p.filename,
        p.slide_count,
        p.file_type
    FROM evaluations e
    JOIN presentations p ON e.presentation_id = p.id
    ORDER BY e.created_at DESC
    LIMIT 10
    """)
    recent_rows = cursor.fetchall()
    recent_evaluations = [dict(r) for r in recent_rows]
    
    # Best-performing presentations
    cursor.execute("""
    SELECT 
        e.id as eval_id,
        e.presentation_id,
        e.mode,
        e.overall_score,
        e.rating_label,
        p.filename,
        p.slide_count
    FROM evaluations e
    JOIN presentations p ON e.presentation_id = p.id
    ORDER BY e.overall_score DESC
    LIMIT 5
    """)
    best_rows = cursor.fetchall()
    best_performing = [dict(r) for r in best_rows]
    
    # Collect critical issues across all evaluations
    cursor.execute("SELECT critical_issues_json FROM evaluations ORDER BY created_at DESC LIMIT 20")
    issue_rows = cursor.fetchall()
    all_issues = []
    for ir in issue_rows:
        if ir["critical_issues_json"]:
            try:
                issues = json.loads(ir["critical_issues_json"])
                all_issues.extend(issues)
            except Exception:
                pass
                
    # Category score averages
    cursor.execute("SELECT category_scores_json FROM evaluations")
    eval_cats = cursor.fetchall()
    cat_accumulator = {}
    for ec in eval_cats:
        if ec["category_scores_json"]:
            try:
                scores = json.loads(ec["category_scores_json"])
                for s in scores:
                    name = s["name"]
                    if name not in cat_accumulator:
                        cat_accumulator[name] = {"total": 0.0, "count": 0}
                    cat_accumulator[name]["total"] += float(s["score"])
                    cat_accumulator[name]["count"] += 1
            except Exception:
                pass
                
    category_analytics = [
        {"name": name, "average_score": round(data["total"] / max(1, data["count"]), 1)}
        for name, data in cat_accumulator.items()
    ]
    
    conn.close()
    
    return {
        "total_analyzed": total_count,
        "average_score": avg_score,
        "recent_evaluations": recent_evaluations,
        "best_performing": best_performing,
        "critical_issues": all_issues[:12],
        "category_analytics": category_analytics[:8]
    }

@router.get("/presentations")
async def list_presentations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        p.*,
        e.overall_score,
        e.rating_label,
        e.verdict
    FROM presentations p
    LEFT JOIN (
        SELECT presentation_id, overall_score, rating_label, verdict, MAX(created_at)
        FROM evaluations GROUP BY presentation_id
    ) e ON p.id = e.presentation_id
    ORDER BY p.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

