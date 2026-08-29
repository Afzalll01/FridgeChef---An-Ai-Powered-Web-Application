import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the backend folder or workspace root if present
backend_dir = Path(__file__).resolve().parent
env_path = backend_dir / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "fridgechef-super-secret-production-key-2026")

    # Database configuration
    # Supports PostgreSQL (Render) and falls back to SQLite for local development
    database_url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI")
    if database_url:
        # SQLAlchemy requires 'postgresql://' instead of legacy 'postgres://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Default SQLite path
        db_path = backend_dir / "database.sqlite"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.as_posix()}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # External APIs
    SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY", "f27dfecc2f80481bb246959ef390881b")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # YOLO AI Model path
    MODEL_PATH = os.getenv(
        "YOLO_MODEL_PATH",
        str(backend_dir / "models_ai" / "fridge_yolov8.pt")
    )

    # Temporary upload folder
    UPLOAD_FOLDER = str(backend_dir / "uploads")

    # CORS configuration
    # Set FRONTEND_URL in Render env to your Vercel deployment URL (e.g. https://fridge-chef.vercel.app)
    FRONTEND_URL = os.getenv("FRONTEND_URL", "")
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
    ]
    if FRONTEND_URL:
        # Support comma-separated origins
        for url in FRONTEND_URL.split(","):
            cleaned = url.strip().rstrip("/")
            if cleaned and cleaned not in ALLOWED_ORIGINS:
                ALLOWED_ORIGINS.append(cleaned)
                ALLOWED_ORIGINS.append(f"{cleaned}/")

    # Server settings
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
