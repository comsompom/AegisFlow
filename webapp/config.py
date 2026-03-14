import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"
    BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000").rstrip("/")
    DEMO_USER = os.environ.get("DEMO_USER", "compliance")
    DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "demo123")
