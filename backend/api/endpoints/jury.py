import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.database import get_db
from backend.ai.provider import ai_provider

router = APIRouter()

class AnswerEvaluationRequest(BaseModel):
    presentation_id: str
    question_id: str
    question_text: str
    evaluator_type: str
    user_answer: str

@router.get("/{presentation_id}")
async def get_jury_questions(presentation_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT jury_questions_json FROM evaluations 
    WHERE presentation_id = ? 
    ORDER BY created_at DESC LIMIT 1
    """, (presentation_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row["jury_questions_json"]:
        raise HTTPException(status_code=404, detail="Jury questions not found for this presentation")
        
    return {
        "presentation_id": presentation_id,
        "questions": json.loads(row["jury_questions_json"])
    }

@router.post("/evaluate-answer")
async def evaluate_jury_answer(req: AnswerEvaluationRequest):
    """Evaluate how well the user defended a question during Jury Simulation."""
    prompt = f"""
Evaluate this student defense answer for an SIH Grand Finale jury defense:
Jury Perspective: {req.evaluator_type}
Question Asked: {req.question_text}
Student's Response: {req.user_answer}

Return a valid JSON response:
{{
  "score": 8.5,
  "verdict": "Strong Defense / Adequate / Vulnerable",
  "critique": "Constructive evaluation of the defense...",
  "strengths": ["Clear technical articulation", "Addressed concurrency"],
  "gaps": ["Did not mention unit testing or fallback strategies"],
  "counter_question": "Immediate follow-up question the evaluator would fire back..."
}}
"""
    system_prompt = (
        "You are an experienced Smart India Hackathon jury chair evaluating a team's live defense. "
        "Be constructive, sharp, and realistic."
    )
    
    parsed, model, err = ai_provider.generate_json_response(prompt, system_prompt)
    if parsed:
        return parsed
        
    # Heuristic evaluator fallback
    words = len(req.user_answer.split())
    if words > 45:
        score = 8.5
        verdict = "Strong Defense"
        critique = "Your answer provides concrete reasoning, mentions architectural safeguards, and demonstrates domain poise."
        strengths = ["Comprehensive technical coverage", "Addresses potential bottlenecks directly"]
        gaps = ["Could quantify benchmark numbers (latency ms or user load)"]
        counter = "What exact latency numbers did you observe during peak test load?"
    elif words > 20:
        score = 7.0
        verdict = "Adequate Defense"
        critique = "You addressed the question surface but missed deeper architectural trade-offs."
        strengths = ["Understands the core concept"]
        gaps = ["Needs more specifics on implementation and fallback protocols"]
        counter = "Can you elaborate on your fallback protocol if the primary service disconnects?"
    else:
        score = 4.5
        verdict = "Vulnerable Defense"
        critique = "The response is too vague or brief. The jury will easily dismantle this answer during live evaluation."
        strengths = ["Basic acknowledgment of the issue"]
        gaps = ["Lacks technical details, tooling names, and proactive justification"]
        counter = "Could you walk us through the exact step-by-step workflow for that?"
        
    return {
        "score": score,
        "verdict": verdict,
        "critique": critique,
        "strengths": strengths,
        "gaps": gaps,
        "counter_question": counter
    }

