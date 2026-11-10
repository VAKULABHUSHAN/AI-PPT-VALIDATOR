import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Resolve project paths
BASE_DIR = Path(__file__).resolve().parent.parent           # D:\AI-PPT-VALIDATOR\backend
PROJECT_ROOT = BASE_DIR.parent                              # D:\AI-PPT-VALIDATOR
ENV_FILE = PROJECT_ROOT / ".env"

# Load root .env file securely on module import
if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)
else:
    load_dotenv()  # Fallback to standard environment search

def resolve_storage_path(env_var_name: str, default_rel_path: Path, base_parent: Path = PROJECT_ROOT) -> Path:
    """Resolve a storage path from environment: supports relative and absolute paths."""
    raw = os.getenv(env_var_name, "").strip()
    if not raw:
        return default_rel_path
    p = Path(raw)
    if p.is_absolute():
        return p
    return base_parent / p

def get_storage_paths():
    """Retrieve normalized storage paths configured via environment variables."""
    storage_dir = resolve_storage_path("STORAGE_DIR", BASE_DIR / "storage", PROJECT_ROOT)
    uploads_dir = resolve_storage_path("UPLOADS_DIR", storage_dir / "uploads", PROJECT_ROOT)
    slides_dir = resolve_storage_path("SLIDES_DIR", storage_dir / "slides", PROJECT_ROOT)
    reports_dir = resolve_storage_path("REPORTS_DIR", storage_dir / "reports", PROJECT_ROOT)
    db_path = resolve_storage_path("DB_PATH", BASE_DIR / "ppt_validator.db", PROJECT_ROOT)
    return storage_dir, uploads_dir, slides_dir, reports_dir, db_path

def ensure_storage_dirs(storage_dir: Path, uploads_dir: Path, slides_dir: Path, reports_dir: Path):
    """Ensure all required storage directories and scratch directories exist on disk."""
    for path in [storage_dir, uploads_dir, slides_dir, reports_dir, storage_dir / "temp"]:
        path.mkdir(parents=True, exist_ok=True)

STORAGE_DIR, UPLOADS_DIR, SLIDES_DIR, REPORTS_DIR, DB_PATH = get_storage_paths()
ensure_storage_dirs(STORAGE_DIR, UPLOADS_DIR, SLIDES_DIR, REPORTS_DIR)

class Settings(BaseModel):
    APP_NAME: str = "PPT Validator AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [".pptx", ".ppt", ".pdf"]
    
    # AI Keys & Providers (loaded from environment)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "gemini")
    
    # Active Models
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Storage Paths (Configured via .env)
    PROJECT_ROOT: Path = PROJECT_ROOT
    BASE_DIR: Path = BASE_DIR
    STORAGE_DIR: Path = STORAGE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    SLIDES_DIR: Path = SLIDES_DIR
    REPORTS_DIR: Path = REPORTS_DIR
    DB_PATH: Path = DB_PATH
    ENV_FILE: Path = ENV_FILE

settings = Settings()

def reload_settings():
    """Reload environment variables from root .env and refresh runtime settings."""
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=True)
    settings.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    settings.DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "gemini")
    settings.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    settings.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    s_dir, u_dir, sl_dir, r_dir, db_p = get_storage_paths()
    settings.STORAGE_DIR = s_dir
    settings.UPLOADS_DIR = u_dir
    settings.SLIDES_DIR = sl_dir
    settings.REPORTS_DIR = r_dir
    settings.DB_PATH = db_p
    ensure_storage_dirs(s_dir, u_dir, sl_dir, r_dir)

def update_env_file(key: str, value: str):
    """
    Securely persist an environment variable key-value pair to the root .env file.
    Does not log or expose the value.
    """
    lines = []
    found = False
    
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"export {key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)
            
    if not found:
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n")
        new_lines.append(f"{key}={value}\n")
        
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    os.environ[key] = value
    reload_settings()
