import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()  # Charge le fichier .env

@dataclass
class Config:
    # PRONOTE
    PRONOTE_PORTAL_URL: str = os.getenv("PRONOTE_PORTAL_URL", "")
    PRONOTE_EDUCONNECT_USERNAME: str = os.getenv("PRONOTE_EDUCONNECT_USERNAME", "")
    PRONOTE_EDUCONNECT_PASSWORD: str = os.getenv("PRONOTE_EDUCONNECT_PASSWORD", "")
    PRONOTE_STUDENT_PROFILE: str = os.getenv("PRONOTE_STUDENT_PROFILE", "eleve")
    PRONOTE_ETABLISSEMENT: str = os.getenv("PRONOTE_ETABLISSEMENT", "Lycée Aragon Picasso")
    PRONOTE_DIRECT_URL: str = os.getenv("PRONOTE_DIRECT_URL", "")

    # NOTION
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
    NOTION_TASK_DATABASE_ID: str = os.getenv("NOTION_TASK_DATABASE_ID", "")
    NOTION_LYCEE_PROJECT_PAGE_ID: str = os.getenv("NOTION_LYCEE_PROJECT_PAGE_ID", "")

    # Options
    DRY_RUN: bool = os.getenv("DRY_RUN", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    NOTION_RATE_LIMIT_DELAY: float = float(os.getenv("NOTION_RATE_LIMIT_DELAY", "0.1"))
    HEADLESS: bool = os.getenv("HEADLESS", "True").lower() == "true"

def get_config():
    """Retourne la configuration validee."""
    config = Config()

    # Validation basique
    if not config.PRONOTE_PORTAL_URL:
        raise ValueError("PRONOTE_PORTAL_URL est requis dans .env")
    if not config.PRONOTE_EDUCONNECT_USERNAME:
        raise ValueError("PRONOTE_EDUCONNECT_USERNAME est requis dans .env")
    if not config.PRONOTE_EDUCONNECT_PASSWORD:
        raise ValueError("PRONOTE_EDUCONNECT_PASSWORD est requis dans .env")
    if not config.NOTION_API_KEY:
        raise ValueError("NOTION_API_KEY est requis dans .env")
    if not config.NOTION_TASK_DATABASE_ID:
        raise ValueError("NOTION_TASK_DATABASE_ID est requis dans .env")
    if not config.NOTION_LYCEE_PROJECT_PAGE_ID:
        raise ValueError("NOTION_LYCEE_PROJECT_PAGE_ID est requis dans .env")

    return config