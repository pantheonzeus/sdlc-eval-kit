import json

from csvcheck import Schema, validate_file
from csvcheck.cli import main

SCHEMA = {"columns": [{"name": "id", "type": "int"}, {"name": "note"}, {"name": "score", "type": "float"}]}

CONTENT = (
    "id,note,score\n"  # line 1
    '1,"first line\n'  # line 2: record starts
    'second line",0.5\n'  # line 3
    "x,plain,1.0\n"  # line 4: bad id
    '2,"a\n'  # line 5: record starts
    "b\n"  # line 6
    'c",oops\n'  # line 7
    "3,plain,2.0\n"  # line 8
)


def _files(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(CONTENT, encoding="utf-8")
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(SCHEMA), encoding="utf-8")
    return csv_path, schema_path


def test_lines_are_record_start_lines(tmp_path):
    csv_path, schema_path = _files(tmp_path)
    errors = validate_file(csv_path, Schema.load(schema_path))
    assert [(e.line, e.column) for e in errors] == [(4, "id"), (5, "score")]


def test_cli_reports_record_start(tmp_path, capsys):
    csv_path, schema_path = _files(tmp_path)
    assert main([str(csv_path), "--schema", str(schema_path)]) == 1
    assert capsys.readouterr().out.splitlines() == [
        "line 4: id: 'x' is not an integer",
        "line 5: score: 'oops' is not a number",
    ]
