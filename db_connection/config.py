import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def default_env_path() -> Path:
    """Return the default path for local credential storage."""
    return Path.home() / "credentials" / "db_connect" / ".env"


def load_env_file(env_path: Path) -> bool:
    """Load environment values from a .env file if it exists."""
    if not env_path.exists():
        return False

    load_dotenv(dotenv_path=env_path, override=False)
    return True


def get_database_url(override_url: Optional[str]) -> str:
    """Resolve the database URL from CLI override or environment."""
    if override_url:
        return override_url

    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL is not set. Provide --database-url or add DATABASE_URL to a .env file."
        )
    return url
