from typing import List, Optional
from pydantic import BaseModel, Field

class Criterion(BaseModel):
    id: str
    name: str
    description: str
    weightage: float  # Percentage, total should sum to 100
    max_score: float = 10.0

class RubricDefinition(BaseModel):
    id: str
    name: str
    description: str
    is_builtin: bool = True
    mode_key: str  # 'sih', 'academic', 'project_review', 'subject', 'research', 'custom'
    criteria: List[Criterion]
    mandatory_sections: List[str] = []
    min_passing_score: float = 60.0
    created_at: Optional[str] = None

class CreateRubricRequest(BaseModel):
    name: str
    description: str
    criteria: List[Criterion]
    mandatory_sections: List[str] = []
    min_passing_score: float = 60.0

