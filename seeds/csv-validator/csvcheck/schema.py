"""Column schema: names, types and required flags."""

import json
from dataclasses import dataclass
from pathlib import Path

TYPES = ("int", "float", "str", "date")


class SchemaError(ValueError):
    """Raised for an invalid schema definition."""


@dataclass(frozen=True)
class Column:
    name: str
    type: str = "str"
    required: bool = True

    def __post_init__(self) -> None:
        if self.type not in TYPES:
            raise SchemaError(f"column {self.name!r}: unknown type {self.type!r}")


@dataclass(frozen=True)
class Schema:
    columns: tuple[Column, ...]

    @property
    def names(self) -> list[str]:
        return [column.name for column in self.columns]

    @classmethod
    def from_dict(cls, data: dict) -> "Schema":
        if not isinstance(data.get("columns"), list) or not data["columns"]:
            raise SchemaError("schema needs a non-empty 'columns' list")
        columns = []
        for entry in data["columns"]:
            if "name" not in entry:
                raise SchemaError(f"column without a name: {entry!r}")
            unknown = set(entry) - {"name", "type", "required"}
            if unknown:
                raise SchemaError(f"column {entry['name']!r}: unknown keys {sorted(unknown)}")
            columns.append(Column(entry["name"], entry.get("type", "str"), entry.get("required", True)))
        names = [column.name for column in columns]
        if len(names) != len(set(names)):
            raise SchemaError("duplicate column names")
        return cls(tuple(columns))

    @classmethod
    def load(cls, path: str | Path) -> "Schema":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
