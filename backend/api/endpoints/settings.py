import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.core.config import settings, update_env_file, reload_settings
from backend.ai.provider import ai_provider
from backend.processors.ppt_converter import get_conversion_diagnostics

router = APIRouter()

class UpdateSettingsRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    default_provider: Optional[str] = None

class TestKeyRequest(BaseModel):
    api_key: Optional[str] = None

@router.get("/")
async def get_settings():
    """
    Returns platform settings.
    CRITICAL SECURITY GUARANTEE: Never returns raw API keys.
    """
    return {
        "gemini_configured": bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 0),
        "openai_configured": bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 0),
        "default_provider": settings.DEFAULT_AI_PROVIDER,
        "gemini_model": settings.GEMINI_MODEL,
        "openai_model": settings.OPENAI_MODEL,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
        "storage": {
            "storage_dir": str(settings.STORAGE_DIR),
            "uploads_dir": str(settings.UPLOADS_DIR),
            "slides_dir": str(settings.SLIDES_DIR),
            "reports_dir": str(settings.REPORTS_DIR),
            "db_path": str(settings.DB_PATH)
        }
    }

@router.post("/")
async def update_settings(req: UpdateSettingsRequest):
    """
    Securely update environment credentials.
    Persists to root .env file and updates memory without touching SQLite or returning keys.
    """
    if req.gemini_api_key is not None and req.gemini_api_key.strip():
        update_env_file("GEMINI_API_KEY", req.gemini_api_key.strip())
        
    if req.openai_api_key is not None and req.openai_api_key.strip():
        update_env_file("OPENAI_API_KEY", req.openai_api_key.strip())
        
    if req.default_provider:
        update_env_file("DEFAULT_AI_PROVIDER", req.default_provider)
        
    # Refresh settings and reload provider clients
    reload_settings()
    ai_provider._init_clients()
    
    return {
        "message": "Configuration updated securely in local environment.",
        "gemini_configured": bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 0),
        "openai_configured": bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 0),
        "default_provider": settings.DEFAULT_AI_PROVIDER
    }

@router.post("/test-gemini")
async def test_gemini_api(req: TestKeyRequest):
    """
    Executes a real lightweight verification request to Google Gemini API.
    Returns status, latency, and sanitized diagnostics without echoing the key.
    """
    return ai_provider.test_gemini_connectivity(test_api_key=req.api_key)

@router.post("/test-openai")
async def test_openai_api(req: TestKeyRequest):
    """
    Executes a real lightweight verification request to OpenAI API.
    """
    return ai_provider.test_openai_connectivity(test_api_key=req.api_key)

@router.get("/diagnostics")
async def get_system_diagnostics():
    """
    Returns platform diagnostics for PPT-to-PDF conversion, AI engines, and storage.
    """
    conv_diag = get_conversion_diagnostics()
    return {
        "conversion_pipeline": conv_diag,
        "storage": {
            "storage_dir": str(settings.STORAGE_DIR),
            "storage_dir_exists": settings.STORAGE_DIR.exists(),
            "uploads_dir": str(settings.UPLOADS_DIR),
            "slides_dir": str(settings.SLIDES_DIR),
            "reports_dir": str(settings.REPORTS_DIR),
            "db_path": str(settings.DB_PATH)
        },
        "ai_engine": {
            "gemini_configured": bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 0),
            "gemini_model": settings.GEMINI_MODEL,
            "openai_configured": bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 0),
            "openai_model": settings.OPENAI_MODEL,
            "default_provider": settings.DEFAULT_AI_PROVIDER,
            "offline_heuristic_available": True
        }
    }
