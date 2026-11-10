import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.core.database import init_db, get_db
from backend.api.routes import api_router
from backend.sample_data import create_sample_sih_pptx
from backend.api.endpoints.upload import process_presentation_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    init_db()
    
    # Check if database is empty; if so, generate a sample presentation for instant preview
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM presentations")
    count = cursor.fetchone()["count"]
    conn.close()
    
    if count == 0:
        try:
            sample_id = "sample-sih-2024"
            sample_file = settings.UPLOADS_DIR / "SIH2024_AgriSense_SmartIrrigation.pptx"
            create_sample_sih_pptx(sample_file)
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO presentations (
                id, filename, file_path, file_type, file_size_bytes, slide_count,
                mode, status, progress_stage, progress_message, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                sample_id,
                "SIH2024_AgriSense_SmartIrrigation.pptx",
                str(sample_file),
                ".pptx",
                os.path.getsize(sample_file),
                7,
                "sih",
                "processing",
                1,
                "Initializing sample evaluation..."
            ))
            conn.commit()
            conn.close()
            
            # Run processing pipeline for the sample
            process_presentation_pipeline(sample_id, sample_file, ".pptx", "sih")
            print(f"[PPT Validator AI] Seeded sample SIH project presentation: {sample_id}")
        except Exception as e:
            print(f"[PPT Validator AI] Could not seed sample data: {e}")
            
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Presentation Evaluation, Quality Assurance & Feedback Platform",
    lifespan=lifespan
)

# Enable CORS for local Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static storage for slide thumbnails, previews, and downloadable reports
app.mount("/static", StaticFiles(directory=str(settings.STORAGE_DIR)), name="static")

# Mount API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

