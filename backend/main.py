
from io import BytesIO
import json

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pptx import Presentation
from sqlalchemy.orm import Session

from database import SessionLocal, PresentationRecord, EvaluationRecord

app = FastAPI(
    title="AI PPT Validator",
    description="Backend API for validating PowerPoint presentations",
    version="1.0.0"
)


# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "AI PPT Validator Backend is running!",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend"
    }


# Upload PPT and extract slide text
@app.post("/api/ppt/extract")
async def extract_ppt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename or not file.filename.lower().endswith(".pptx"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a .pptx file"
        )

    content = await file.read(20 * 1024 * 1024 + 1)

    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds 20 MB")

    try:
        presentation = Presentation(BytesIO(content))
        slides_data = []

        for slide_number, slide in enumerate(presentation.slides, start=1):
            slide_text = []

            for shape in slide.shapes:
                if shape.has_text_frame:
                    text = shape.text.strip()
                    if text:
                        slide_text.append(text)

            if slide.shapes.title and slide.shapes.title.text.strip():
                title = slide.shapes.title.text.strip()
            else:
                title = slide_text[0] if slide_text else "Untitled"

            slides_data.append({
                "slide_number": slide_number,
                "title": title,
                "text": slide_text
            })

        # Save presentation in database
        record = PresentationRecord(
            filename=file.filename,
            total_slides=len(presentation.slides),
            slides_json=json.dumps(slides_data, ensure_ascii=False)
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "presentation_id": record.id,
            "filename": record.filename,
            "total_slides": record.total_slides,
            "slides": slides_data,
            "message": "PPT extracted and saved successfully"
        }

    except Exception as error:
        db.rollback()
        if isinstance(error, HTTPException):
            raise error
        raise HTTPException(
            status_code=400,
            detail="Unable to read or save this PowerPoint file"
        )


# Get all uploaded presentations
@app.get("/api/presentations")
def get_presentations(db: Session = Depends(get_db)):
    records = db.query(PresentationRecord).order_by(
        PresentationRecord.id.desc()
    ).all()

    return [
        {
            "presentation_id": record.id,
            "filename": record.filename,
            "total_slides": record.total_slides,
            "uploaded_at": record.uploaded_at.isoformat()
        }
        for record in records
    ]


# Get one presentation by ID
@app.get("/api/presentations/{presentation_id}")
def get_presentation(
    presentation_id: int,
    db: Session = Depends(get_db)
):
    record = db.query(PresentationRecord).filter(
        PresentationRecord.id == presentation_id
    ).first()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Presentation not found"
        )

    return {
        "presentation_id": record.id,
        "filename": record.filename,
        "total_slides": record.total_slides,
        "uploaded_at": record.uploaded_at.isoformat(),
        "slides": json.loads(record.slides_json)
    }


# Evaluate a presentation (temporary mock evaluator)
@app.post("/api/ppt/evaluate/{presentation_id}")
def evaluate_presentation(
    presentation_id: int,
    db: Session = Depends(get_db)
):
    # Find the uploaded presentation
    record = db.query(PresentationRecord).filter(
        PresentationRecord.id == presentation_id
    ).first()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Presentation not found"
        )

    # Retrieve extracted slide content
    slides = json.loads(record.slides_json)

    # TEMPORARY TEST DATA - NOT REAL AI EVALUATION
    evaluation_result = {
        "evaluation_mode": "mock",
        "overall_score": 75,
        "summary": "This is temporary test feedback, not an actual AI evaluation.",
        "slide_feedback": [
            {
                "slide_number": slide["slide_number"],
                "score": 75,
                "issues": ["Mock issue for testing"],
                "suggestions": ["Mock suggestion for testing"]
            }
            for slide in slides
        ],
        "improvements": [
            "Temporary improvement suggestion for testing"
        ]
    }

    # Save evaluation in SQLite
    evaluation_record = EvaluationRecord(
        presentation_id=record.id,
        overall_score=evaluation_result["overall_score"],
        results_json=json.dumps(
            evaluation_result,
            ensure_ascii=False
        )
    )

    try:
        db.add(evaluation_record)
        db.commit()
        db.refresh(evaluation_record)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save evaluation"
        )

    return {
        "evaluation_id": evaluation_record.id,
        "presentation_id": record.id,
        "filename": record.filename,
        "overall_score": evaluation_record.overall_score,
        "results": evaluation_result,
        "message": "Mock evaluation saved successfully"
    }

# Get a saved evaluation report
@app.get("/api/evaluations/{evaluation_id}")
def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    evaluation = db.query(EvaluationRecord).filter(
        EvaluationRecord.id == evaluation_id
    ).first()

    if evaluation is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found"
        )

    return {
        "evaluation_id": evaluation.id,
        "presentation_id": evaluation.presentation_id,
        "overall_score": evaluation.overall_score,
        "results": json.loads(evaluation.results_json),
        "created_at": evaluation.created_at.isoformat()
    }