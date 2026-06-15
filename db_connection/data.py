import csv
import json
from pathlib import Path
from typing import Any, List, Literal, Optional


DataFormat = Literal["json", "csv"]


def load_query(query: str, query_file: Optional[Path]) -> str:
    """Load SQL from a file or return the provided query string."""
    if query_file is not None:
        return query_file.read_text(encoding="utf-8")
    return query


def infer_data_format(data_file: Path, explicit_format: Optional[DataFormat]) -> DataFormat:
    """Guess the data format from the file extension unless one is provided."""
    if explicit_format is not None:
        return explicit_format

    suffix = data_file.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"

    raise ValueError(
        "Could not infer data format from file extension. Use --data-format json|csv."
    )


def load_data_file(data_file: Path, data_format: Optional[DataFormat]) -> Any:
    """Load JSON or CSV data from disk for parameterized query execution."""
    actual_format = infer_data_format(data_file, data_format)
    if actual_format == "json":
        return json.loads(data_file.read_text(encoding="utf-8"))

    rows: List[dict[str, str]] = []
    with data_file.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = [row for row in reader]
    return rows
