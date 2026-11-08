from csvcheck.cli import main


def test_cli_valid(write, schema_file, capsys):
    path = write("ok.csv", "id,email,score,signup\n1,a@example.com,,\n")
    assert main([str(path), "--schema", str(schema_file)]) == 0
    assert capsys.readouterr().out == ""


def test_cli_errors(write, schema_file, capsys):
    path = write("bad.csv", "id,email,score,signup\nx,a@example.com,,\n")
    assert main([str(path), "--schema", str(schema_file)]) == 1
    assert capsys.readouterr().out == "line 2: id: 'x' is not an integer\n"


def test_cli_bad_schema(write, capsys):
    path = write("ok.csv", "a\n1\n")
    schema = write("schema.json", {"columns": []})
    assert main([str(path), "--schema", str(schema)]) == 2
    assert "schema error" in capsys.readouterr().err
