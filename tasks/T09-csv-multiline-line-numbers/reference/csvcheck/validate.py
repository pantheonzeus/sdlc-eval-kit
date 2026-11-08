"""Row and file validation."""

import csv
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from csvcheck.schema import Column, Schema


@dataclass(frozen=True)
class ValidationError:
    line: int
    column: str
    message: str

    def __str__(self) -> str:
        return f"line {self.line}: {self.column}: {self.message}"


def _check_value(column: Column, value: str) -> str | None:
    if value == "":
        return "missing value" if column.required else None
    if column.type == "int":
        try:
            int(value)
        except ValueError:
            return f"{value!r} is not an integer"
    elif column.type == "float":
        try:
            float(value)
        except ValueError:
            return f"{value!r} is not a number"
    elif column.type == "date":
        try:
            date.fromisoformat(value)
        except ValueError:
            return f"{value!r} is not a date (YYYY-MM-DD)"
    return None


def validate_rows(rows: Iterable[tuple[int, dict[str, str]]], schema: Schema) -> list[ValidationError]:
    """Validate (line number, row) pairs and return every error found."""
    errors = []
    for line, row in rows:
        for column in schema.columns:
            message = _check_value(column, row.get(column.name) or "")
            if message:
                errors.append(ValidationError(line, column.name, message))
    return errors


def validate_file(path: str | Path, schema: Schema) -> list[ValidationError]:
    """Validate a CSV file with a header row. Line numbers are 1-based file lines."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [name for name in schema.names if name not in header]
        if missing:
            return [ValidationError(1, name, "column missing from header") for name in missing]
        return validate_rows(_numbered(reader), schema)


def _numbered(reader: csv.DictReader) -> Iterable[tuple[int, dict[str, str]]]:
    """Pair each record with the file line it starts on, also for multi-line quoted fields."""
    start = reader.line_num + 1
    for row in reader:
        yield start, row
        start = reader.line_num + 1
