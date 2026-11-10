import os
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
from backend.core.config import settings
from backend.schemas.presentation import SlideContent
from backend.processors.ppt_converter import convert_presentation_to_pdf

def render_pdf_slides(pdf_path: Path, output_dir: Path) -> List[str]:
    """Render PDF pages into PNG images using PyMuPDF, preserving exact 1-based slide order."""
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    image_paths = []
    
    for i in range(len(doc)):
        page = doc[i]
        # Render page at 150 DPI for crisp visual inspection and UI display
        zoom = 150 / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_file = output_dir / f"slide_{i+1}.png"
        pix.save(str(out_file))
        image_paths.append(str(out_file))
        
    doc.close()
    return image_paths

def render_presentation_slides(file_path: Path, file_ext: str, slides: List[SlideContent], output_dir: Path) -> List[str]:
    """
    Robust pipeline for rendering slides:
    1. If PDF: Directly renders pages via PyMuPDF at 150 DPI.
    2. If PPT/PPTX:
       - Attempts headless conversion to temporary PDF (via LibreOffice or PowerPoint COM).
       - If converted, renders pages via PyMuPDF for authentic visual styling.
       - Cleans up temporary PDF.
       - If conversion unavailable, renders high-fidelity slide cards with Pillow.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if file_ext == ".pdf":
        return render_pdf_slides(file_path, output_dir)
        
    # For PPT / PPTX:
    temp_dir = settings.STORAGE_DIR / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    converted_pdf = convert_presentation_to_pdf(file_path, temp_dir)
    
    if converted_pdf and converted_pdf.exists():
        try:
            image_paths = render_pdf_slides(converted_pdf, output_dir)
            # Clean up temporary PDF
            try:
                os.remove(str(converted_pdf))
            except Exception:
                pass
            return image_paths
        except Exception as e:
            # Fall back to Pillow card renderer if PyMuPDF rendering of converted PDF encounters an issue
            pass
            
    # Native fallback: high-fidelity presentation preview cards
    return render_pptx_slide_cards(slides, output_dir)

def render_pptx_slide_cards(slides: List[SlideContent], output_dir: Path) -> List[str]:
    """
    Render high-fidelity presentation preview cards for PPTX slides using PIL.
    Renders 16:9 1280x720 images with dark presentation canvas, titles, bullets, tables, and metrics.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []
    
    width = 1280
    height = 720
    
    for slide in slides:
        img = Image.new("RGB", (width, height), color=(15, 18, 26))
        draw = ImageDraw.Draw(img)
        
        # Draw slide frame background styling
        draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(35, 42, 60), width=2)
        
        # Slide Header Banner
        draw.rectangle([(40, 40), (width - 40, 110)], fill=(22, 28, 42))
        
        # Slide Number Badge
        draw.rectangle([(50, 52), (160, 98)], fill=(37, 99, 235))
        draw.text((65, 65), f"SLIDE {slide.slide_number:02d}", fill=(255, 255, 255))
        
        # Slide Title
        title_text = slide.title if slide.title and slide.title.strip() else f"Slide {slide.slide_number}"
        if len(title_text) > 60:
            title_text = title_text[:57] + "..."
        draw.text((180, 65), title_text, fill=(241, 245, 249))
        
        # Word count & Visual Badge
        if slide.visual_metrics:
            badge_text = f"Words: {slide.visual_metrics.word_count} | {slide.visual_metrics.visual_rating}"
            draw.text((width - 320, 65), badge_text, fill=(148, 163, 184))
            
        # Draw content body
        curr_y = 140
        
        # Bullet points and text blocks
        items_to_render = []
        if slide.bullet_points:
            items_to_render.extend([f"•  {b}" for b in slide.bullet_points])
        elif slide.body_texts:
            items_to_render.extend([f"•  {t}" for t in slide.body_texts])
            
        if not items_to_render and slide.raw_text:
            lines = [l.strip() for l in slide.raw_text.split("\n") if l.strip() and l.strip() != slide.title]
            items_to_render.extend([f"•  {l}" for l in lines[:10]])
            
        for item in items_to_render[:8]:  # show top 8 bullets
            if curr_y > height - 120:
                break
            
            # Simple word-wrapping
            words = item.split()
            line = ""
            for w in words:
                if len(line + " " + w) > 85:
                    draw.text((60, curr_y), line, fill=(226, 232, 240))
                    curr_y += 30
                    line = "     " + w
                else:
                    line = (line + " " + w).strip() if not line else line + " " + w
            if line:
                draw.text((60, curr_y), line, fill=(226, 232, 240))
                curr_y += 36
                
        # Draw table preview if tables exist
        if slide.tables and curr_y < height - 160:
            tbl = slide.tables[0]
            draw.text((60, curr_y), f"[Table: {tbl.rows} rows x {tbl.cols} cols]", fill=(56, 189, 248))
            curr_y += 30
            # Render first 2 rows of table
            for r_idx, row in enumerate(tbl.data[:2]):
                row_str = " | ".join(row[:4])
                draw.rectangle([(60, curr_y), (width - 60, curr_y + 26)], fill=(28, 35, 51), outline=(45, 55, 75))
                draw.text((70, curr_y + 4), row_str[:100], fill=(203, 213, 225))
                curr_y += 30
                
        # Draw image indicator if present
        if slide.image_count > 0:
            draw.rectangle([(width - 240, height - 90), (width - 60, height - 50)], fill=(30, 41, 59), outline=(51, 65, 85))
            draw.text((width - 225, height - 76), f"📷 {slide.image_count} Embedded Images", fill=(56, 189, 248))
            
        # Draw footer
        draw.line([(40, height - 40), (width - 40, height - 40)], fill=(35, 42, 60), width=1)
        draw.text((60, height - 32), "PPT Validator AI • Evaluation Slide Preview", fill=(100, 116, 139))
        
        out_file = output_dir / f"slide_{slide.slide_number}.png"
        img.save(str(out_file))
        image_paths.append(str(out_file))
        
    return image_paths
