import pytest
from csvcheck import Column, Schema, SchemaError, ValidationError, validate_file

SCHEMA = {
    "columns": [
        {"name": "id", "type": "int"},
        {"name": "status", "allowed": ["active", "paused"]},
        {"name": "tier", "allowed": ["gold", "silver"], "required": False},
    ]
}


def test_column_field():
    schema = Schema.from_dict(SCHEMA)
    assert schema.columns[1].allowed == ("active", "paused")
    assert Column("x").allowed is None


def test_value_outside_list(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id,status,tier\n1,active,gold\n2,closed,\n3,paused,bronze\n", encoding="utf-8")
    assert validate_file(path, Schema.from_dict(SCHEMA)) == [
        ValidationError(3, "status", "'closed' is not one of: active, paused"),
        ValidationError(4, "tier", "'bronze' is not one of: gold, silver"),
    ]


def test_empty_follows_required(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id,status,tier\n1,,\n", encoding="utf-8")
    assert validate_file(path, Schema.from_dict(SCHEMA)) == [ValidationError(2, "status", "missing value")]


@pytest.mark.parametrize("allowed", [[], "active", [1, 2], None])
def test_invalid_allowed(allowed):
    with pytest.raises(SchemaError):
        Schema.from_dict({"columns": [{"name": "status", "allowed": allowed}]})
