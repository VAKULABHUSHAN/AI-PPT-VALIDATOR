from pathlib import Path
from typing import List
import fitz  # PyMuPDF
from backend.schemas.presentation import SlideContent
from backend.processors.visual_analyzer import analyze_slide_visuals

def extract_pdf_content(pdf_path: Path) -> List[SlideContent]:
    doc = fitz.open(str(pdf_path))
    extracted_slides: List[SlideContent] = []
    
    for idx, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
        
        title = ""
        body_texts: List[str] = []
        bullets: List[str] = []
        
        # Sort blocks top-to-bottom
        sorted_blocks = sorted(blocks, key=lambda b: b[1])
        
        # First text block usually contains the title
        for b in sorted_blocks:
            if b[6] == 0:  # text block
                b_text = b[4].strip()
                if not b_text:
                    continue
                if not title and len(b_text) < 100:
                    title = b_text.split("\n")[0].strip()
                    # Add remainder of block if any
                    remainder = "\n".join(b_text.split("\n")[1:]).strip()
                    if remainder:
                        body_texts.append(remainder)
                else:
                    lines = b_text.split("\n")
                    for l in lines:
                        l_clean = l.strip()
                        if not l_clean:
                            continue
                        if l_clean.startswith(("-", "•", "*", "1.", "2.", "3.", "4.", "5.")):
                            bullets.append(l_clean.lstrip("-•* ").strip())
                        else:
                            body_texts.append(l_clean)
                            
        # Image list
        image_list = page.get_images(full=True)
        image_count = len(image_list)
        
        # Hyperlinks
        links = []
        for link in page.get_links():
            if "uri" in link:
                links.append(link["uri"])
                
        raw_text = text if text else (f"{title}\n" + "\n".join(body_texts))
        
        visuals = analyze_slide_visuals(
            raw_text=raw_text,
            bullets=bullets,
            shape_count=len(blocks),
            image_count=image_count,
            table_count=0
        )
        
        extracted_slides.append(SlideContent(
            slide_number=idx,
            title=title if title else f"Slide {idx}",
            body_texts=body_texts,
            bullet_points=bullets,
            tables=[],
            speaker_notes=None,
            hyperlinks=links,
            image_count=image_count,
            shape_count=len(blocks),
            raw_text=raw_text,
            visual_metrics=visuals
        ))
        
    doc.close()
    return extracted_slides

