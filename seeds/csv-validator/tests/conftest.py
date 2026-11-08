import json

import pytest


@pytest.fixture
def write(tmp_path):
    """Write a file under tmp_path and return its path."""

    def _write(name, content):
        path = tmp_path / name
        if isinstance(content, (dict, list)):
            content = json.dumps(content)
        path.write_text(content, encoding="utf-8")
        return path

    return _write


@pytest.fixture
def schema_file(write):
    return write(
        "schema.json",
        {
            "columns": [
                {"name": "id", "type": "int"},
                {"name": "email"},
                {"name": "score", "type": "float", "required": False},
                {"name": "signup", "type": "date", "required": False},
            ]
        },
    )
