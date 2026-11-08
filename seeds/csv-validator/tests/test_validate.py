from csvcheck import Schema, ValidationError, validate_file


def test_valid_file(write, schema_file):
    path = write("ok.csv", "id,email,score,signup\n1,a@example.com,0.5,2026-01-02\n2,b@example.com,,\n")
    assert validate_file(path, Schema.load(schema_file)) == []


def test_type_errors_reported_with_line(write, schema_file):
    path = write("bad.csv", "id,email,score,signup\n1,a@example.com,x,2026-01-02\nz,b@example.com,1,2026-13-01\n")
    errors = validate_file(path, Schema.load(schema_file))
    assert errors == [
        ValidationError(2, "score", "'x' is not a number"),
        ValidationError(3, "id", "'z' is not an integer"),
        ValidationError(3, "signup", "'2026-13-01' is not a date (YYYY-MM-DD)"),
    ]


def test_missing_required_value(write, schema_file):
    path = write("missing.csv", "id,email,score,signup\n1,,,\n")
    assert [str(e) for e in validate_file(path, Schema.load(schema_file))] == ["line 2: email: missing value"]


def test_missing_header_column(write, schema_file):
    path = write("header.csv", "id,score\n1,2\n")
    errors = validate_file(path, Schema.load(schema_file))
    assert [(e.line, e.column) for e in errors] == [(1, "email"), (1, "signup")]
