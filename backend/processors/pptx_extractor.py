from pathlib import Path
from typing import List
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from backend.schemas.presentation import SlideContent, TableData
from backend.processors.visual_analyzer import analyze_slide_visuals

def extract_pptx_content(pptx_path: Path) -> List[SlideContent]:
    prs = Presentation(str(pptx_path))
    extracted_slides: List[SlideContent] = []
    
    for idx, slide in enumerate(prs.slides, start=1):
        title = ""
        body_texts: List[str] = []
        bullets: List[str] = []
        tables: List[TableData] = []
        hyperlinks: List[str] = []
        image_count = 0
        shape_count = len(slide.shapes)
        
        # Check slide title shape
        if slide.shapes.title and slide.shapes.title.has_text_frame:
            title = slide.shapes.title.text_frame.text.strip()
            
        for shape in slide.shapes:
            # Check for embedded picture
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                image_count += 1
                
            # Check for tables
            if shape.has_table:
                table_obj = shape.table
                table_matrix: List[List[str]] = []
                for row in table_obj.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_matrix.append(row_data)
                tables.append(TableData(
                    rows=len(table_obj.rows),
                    cols=len(table_obj.columns),
                    data=table_matrix
                ))
                
            # Check for text frame
            if shape.has_text_frame:
                # If title was not yet found, check if this is the title shape
                if not title and shape == slide.shapes.title:
                    title = shape.text_frame.text.strip()
                    continue
                
                for paragraph in shape.text_frame.paragraphs:
                    p_text = paragraph.text.strip()
                    if not p_text:
                        continue
                    
                    # Hyperlink check
                    for run in paragraph.runs:
                        if run.hyperlink and run.hyperlink.address:
                            hyperlinks.append(run.hyperlink.address)
                            
                    # Distinguish title if still empty
                    if not title and len(p_text) < 80 and not bullets and not body_texts:
                        title = p_text
                        continue
                        
                    # Paragraph bullet level or text
                    if paragraph.level > 0 or p_text.startswith(("-", "•", "*", "1.", "2.", "3.", "4.", "5.")):
                        cleaned_bullet = p_text.lstrip("-•* ").strip()
                        bullets.append(cleaned_bullet)
                    else:
                        body_texts.append(p_text)
                        
        # Extract speaker notes if available
        speaker_notes = None
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes_txt = slide.notes_slide.notes_text_frame.text.strip()
            if notes_txt:
                speaker_notes = notes_txt
                
        # Build raw text
        all_text_elements = []
        if title:
            all_text_elements.append(f"Title: {title}")
        if bullets:
            all_text_elements.extend([f"• {b}" for b in bullets])
        if body_texts:
            all_text_elements.extend(body_texts)
        if tables:
            for t in tables:
                all_text_elements.append("\n".join([" | ".join(row) for row in t.data]))
        if speaker_notes:
            all_text_elements.append(f"Speaker Notes: {speaker_notes}")
            
        raw_text = "\n".join(all_text_elements)
        
        # Analyze visuals
        visuals = analyze_slide_visuals(
            raw_text=raw_text,
            bullets=bullets,
            shape_count=shape_count,
            image_count=image_count,
            table_count=len(tables)
        )
        
        extracted_slides.append(SlideContent(
            slide_number=idx,
            title=title if title else f"Slide {idx}",
            body_texts=body_texts,
            bullet_points=bullets,
            tables=tables,
            speaker_notes=speaker_notes,
            hyperlinks=hyperlinks,
            image_count=image_count,
            shape_count=shape_count,
            raw_text=raw_text,
            visual_metrics=visuals
        ))
        
    return extracted_slides

