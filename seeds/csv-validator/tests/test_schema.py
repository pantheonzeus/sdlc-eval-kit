import pytest
from csvcheck import Column, Schema, SchemaError


def test_from_dict_defaults():
    schema = Schema.from_dict({"columns": [{"name": "a"}, {"name": "b", "type": "int", "required": False}]})
    assert schema.columns == (Column("a", "str", True), Column("b", "int", False))
    assert schema.names == ["a", "b"]


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"columns": []},
        {"columns": [{"type": "int"}]},
        {"columns": [{"name": "a", "type": "bool"}]},
        {"columns": [{"name": "a"}, {"name": "a"}]},
        {"columns": [{"name": "a", "colour": "red"}]},
    ],
)
def test_invalid_schemas(data):
    with pytest.raises(SchemaError):
        Schema.from_dict(data)


def test_load(schema_file):
    assert Schema.load(schema_file).names == ["id", "email", "score", "signup"]
