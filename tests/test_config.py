import os
from pathlib import Path

import pytest

from db_connection.config import default_env_path, get_database_url, load_env_file


def test_default_env_path_is_credentials_db_connect() -> None:
    path = default_env_path()
    assert path.parts[-3:] == ("credentials", "db_connect", ".env")


def test_load_env_file_reads_database_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=postgresql://testuser:test@localhost/testdb\n")

    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert load_env_file(env_file)
    assert os.getenv("DATABASE_URL") == "postgresql://testuser:test@localhost/testdb"


def test_load_env_file_missing(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    assert not load_env_file(env_file)


def test_get_database_url_prefers_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_database_url("postgresql://override") == "postgresql://override"


def test_get_database_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://env")
    assert get_database_url(None) == "postgresql://env"


def test_get_database_url_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError):
        get_database_url(None)
