from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class CategoryScore(BaseModel):
    criterion_id: str
    name: str
    score: float            # e.g. 8.5 out of 10
    max_score: float = 10.0
    weightage: float        # e.g. 15%
    weighted_score: float   # (score / max_score) * weightage
    explanation: str
    evidence: str
    recommendation: str

class SlideFeedback(BaseModel):
    slide_number: int
    slide_title: str
    purpose: str
    content_score: float    # 0 to 10
    technical_score: float  # 0 to 10
    visual_score: float     # 0 to 10
    overall_score: float    # 0 to 10
    severity: str           # "Critical", "High", "Medium", "Low"
    issues: List[str] = []
    missing_info: List[str] = []
    recommendations: List[str] = []
    suggested_rewrite: Optional[str] = None
    preview_image_url: str = ""

class JuryQuestion(BaseModel):
    id: str
    evaluator_type: str    # "Technical Expert", "Innovation Evaluator", "Problem Domain Expert", "Implementation Feasibility Evaluator", "Project Impact Evaluator"
    question: str
    reason: str
    difficulty: str        # "Easy", "Moderate", "Tough", "Challenging"
    relevant_slide: int
    good_answer_criteria: List[str] = []
    suggested_answer: str

class EvaluationResult(BaseModel):
    id: str
    presentation_id: str
    mode: str
    ai_mode_applied: str = "Offline heuristic evaluation"  # "Full AI evaluation", "Hybrid AI + rule-based evaluation", "Offline heuristic evaluation"
    ai_model_name: Optional[str] = None
    overall_score: float    # 0 to 100
    rating_label: str       # "Excellent", "Very Good", "Good", "Needs Improvement", "Weak", "Critical Improvements Required"
    verdict: str
    summary_text: str
    category_scores: List[CategoryScore] = []
    slide_feedback: List[SlideFeedback] = []
    critical_issues: List[str] = []
    major_improvements: List[str] = []
    minor_improvements: List[str] = []
    strengths: List[str] = []
    jury_questions: List[JuryQuestion] = []
    created_at: str
