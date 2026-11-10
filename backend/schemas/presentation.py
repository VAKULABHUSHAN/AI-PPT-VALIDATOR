from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class TableCell(BaseModel):
    text: str
    row: int
    col: int

class TableData(BaseModel):
    rows: int
    cols: int
    data: List[List[str]] = []

class VisualMetrics(BaseModel):
    word_count: int = 0
    character_count: int = 0
    density_ratio: float = 0.0  # words per slide area estimate
    bullet_count: int = 0
    font_size_score: float = 8.0  # 0 to 10
    contrast_score: float = 8.0   # 0 to 10
    layout_score: float = 8.0     # 0 to 10
    visual_rating: str = "Good"   # "Excellent", "Good", "Needs Improvement"

class SlideContent(BaseModel):
    slide_number: int
    title: str = "Untitled Slide"
    body_texts: List[str] = []
    bullet_points: List[str] = []
    tables: List[TableData] = []
    speaker_notes: Optional[str] = None
    hyperlinks: List[str] = []
    image_count: int = 0
    shape_count: int = 0
    preview_image_url: str = ""
    visual_metrics: Optional[VisualMetrics] = None
    raw_text: str = ""

class PresentationInfo(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    slide_count: int = 0
    mode: str
    status: str  # 'uploaded', 'processing', 'completed', 'failed'
    progress_stage: int = 0
    progress_message: str = ""
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    slides: List[SlideContent] = []

