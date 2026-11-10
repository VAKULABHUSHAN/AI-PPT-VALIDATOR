from typing import List, Dict, Any
from backend.schemas.presentation import VisualMetrics

def analyze_slide_visuals(raw_text: str, bullets: List[str], shape_count: int, image_count: int, table_count: int) -> VisualMetrics:
    words = raw_text.split()
    word_count = len(words)
    char_count = len(raw_text)
    bullet_count = len(bullets)
    
    # Calculate density ratio (approximate words per slide standard area)
    # Recommended words per presentation slide is 20-50 words. > 100 is high density.
    if word_count == 0:
        density_ratio = 0.0
        font_score = 7.0
        layout_score = 6.0
        contrast_score = 8.0
        rating = "Low Content"
    elif word_count <= 45:
        density_ratio = word_count / 50.0
        font_score = 9.5
        layout_score = 9.0
        contrast_score = 9.0
        rating = "Excellent"
    elif word_count <= 85:
        density_ratio = word_count / 50.0
        font_score = 8.0
        layout_score = 8.0
        contrast_score = 8.5
        rating = "Good"
    elif word_count <= 140:
        density_ratio = word_count / 50.0
        font_score = 6.0
        layout_score = 6.0
        contrast_score = 7.5
        rating = "High Density"
    else:
        density_ratio = word_count / 50.0
        font_score = 4.0
        layout_score = 4.5
        contrast_score = 6.5
        rating = "Wall of Text / Overcrowded"
        
    # Visual balance adjustments
    if image_count > 0 or table_count > 0:
        layout_score = min(10.0, layout_score + 1.0)
    
    if bullet_count > 7:
        layout_score = max(3.0, layout_score - 1.5)
        
    return VisualMetrics(
        word_count=word_count,
        character_count=char_count,
        density_ratio=round(density_ratio, 2),
        bullet_count=bullet_count,
        font_size_score=round(font_score, 1),
        contrast_score=round(contrast_score, 1),
        layout_score=round(layout_score, 1),
        visual_rating=rating
    )

