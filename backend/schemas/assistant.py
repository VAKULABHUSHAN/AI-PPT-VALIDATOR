from typing import List, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    id: str
    role: str  # "user" or "assistant"
    content: str
    cited_slides: List[int] = []
    created_at: str

class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = None  # "gemini", "openai", "heuristic"

