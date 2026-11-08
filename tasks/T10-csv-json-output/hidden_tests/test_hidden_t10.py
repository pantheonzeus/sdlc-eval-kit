import json

import pytest
from csvcheck.cli import main

SCHEMA = {"columns": [{"name": "id", "type": "int"}, {"name": "email"}]}


@pytest.fixture
def files(tmp_path):
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps(SCHEMA), encoding="utf-8")
    bad = tmp_path / "bad.csv"
    bad.write_text("id,email\nx,a@example.com\n2,\n", encoding="utf-8")
    good = tmp_path / "good.csv"
    good.write_text("id,email\n1,a@example.com\n", encoding="utf-8")
    return schema, bad, good


def test_json_errors(files, capsys):
    schema, bad, _ = files
    assert main([str(bad), "--schema", str(schema), "--format", "json"]) == 1
    assert json.loads(capsys.readouterr().out) == [
        {"line": 2, "column": "id", "message": "'x' is not an integer"},
        {"line": 3, "column": "email", "message": "missing value"},
    ]


def test_json_valid(files, capsys):
    schema, _, good = files
    assert main([str(good), "--schema", str(schema), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out) == []


def test_text_default_unchanged(files, capsys):
    schema, bad, _ = files
    assert main([str(bad), "--schema", str(schema)]) == 1
    assert capsys.readouterr().out == "line 2: id: 'x' is not an integer\nline 3: email: missing value\n"


def test_unknown_format_rejected(files):
    schema, bad, _ = files
    with pytest.raises(SystemExit):
        main([str(bad), "--schema", str(schema), "--format", "xml"])
