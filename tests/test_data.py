import json
from pathlib import Path

import pytest

from db_connection.data import load_data_file, load_query


def test_load_query_returns_string() -> None:
    assert load_query("select 1", None) == "select 1"


def test_load_query_from_file(tmp_path: Path) -> None:
    query_file = tmp_path / "test.sql"
    query_file.write_text("SELECT 1;", encoding="utf-8")
    assert load_query("SELECT 2;", query_file) == "SELECT 1;"


def test_load_json_file(tmp_path: Path) -> None:
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps({"name": "Alice"}), encoding="utf-8")
    assert load_data_file(data_file, None) == {"name": "Alice"}


def test_load_csv_file(tmp_path: Path) -> None:
    data_file = tmp_path / "data.csv"
    data_file.write_text("name,email\nAlice,alice@example.com\n", encoding="utf-8")
    assert load_data_file(data_file, None) == [{"name": "Alice", "email": "alice@example.com"}]


def test_load_data_file_unknown_extension(tmp_path: Path) -> None:
    data_file = tmp_path / "data.txt"
    data_file.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError):
        load_data_file(data_file, None)
