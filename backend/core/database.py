import sqlite3
import json
from typing import Any, Optional
from datetime import datetime
from backend.core.config import settings

def get_db():
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Presentations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS presentations (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        slide_count INTEGER DEFAULT 0,
        mode TEXT NOT NULL,
        status TEXT NOT NULL, -- 'uploaded', 'processing', 'completed', 'failed'
        progress_stage INTEGER DEFAULT 0,
        progress_message TEXT DEFAULT '',
        error_message TEXT DEFAULT '',
        metadata_json TEXT DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    
    # Evaluations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id TEXT PRIMARY KEY,
        presentation_id TEXT NOT NULL,
        mode TEXT NOT NULL,
        ai_mode_applied TEXT DEFAULT 'Offline heuristic evaluation',
        ai_model_name TEXT DEFAULT '',
        overall_score REAL NOT NULL,
        rating_label TEXT NOT NULL,
        verdict TEXT NOT NULL,
        summary_text TEXT NOT NULL,
        category_scores_json TEXT NOT NULL,
        slide_feedback_json TEXT NOT NULL,
        critical_issues_json TEXT NOT NULL,
        major_improvements_json TEXT NOT NULL,
        minor_improvements_json TEXT NOT NULL,
        strengths_json TEXT NOT NULL,
        jury_questions_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (presentation_id) REFERENCES presentations(id)
    );
    """)
    
    # Run column migrations for existing databases
    for col_def in [
        ("ai_mode_applied", "TEXT DEFAULT 'Offline heuristic evaluation'"),
        ("ai_model_name", "TEXT DEFAULT ''")
    ]:
        try:
            cursor.execute(f"ALTER TABLE evaluations ADD COLUMN {col_def[0]} {col_def[1]};")
        except sqlite3.OperationalError:
            pass  # column already exists
            
    # Custom Rubrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rubrics (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        is_builtin INTEGER DEFAULT 0,
        mode_key TEXT NOT NULL,
        criteria_json TEXT NOT NULL,
        mandatory_sections_json TEXT NOT NULL,
        min_passing_score REAL DEFAULT 60.0,
        created_at TEXT NOT NULL
    );
    """)
    
    # Assistant Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assistant_messages (
        id TEXT PRIMARY KEY,
        presentation_id TEXT NOT NULL,
        role TEXT NOT NULL, -- 'user', 'assistant'
        content TEXT NOT NULL,
        cited_slides_json TEXT DEFAULT '[]',
        created_at TEXT NOT NULL,
        FOREIGN KEY (presentation_id) REFERENCES presentations(id)
    );
    """)
    
    conn.commit()
    conn.close()

# Initialize DB on module load
init_db()
