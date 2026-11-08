# csv-validator

Validate a CSV file against a JSON column schema.

```json
{"columns": [
  {"name": "id", "type": "int"},
  {"name": "email", "type": "str"},
  {"name": "signup", "type": "date", "required": false}
]}
```

```console
$ python -m csvcheck customers.csv --schema schema.json
line 4: signup: '2026-13-01' is not a date (YYYY-MM-DD)
```

Exit code 0 when the file is valid, 1 when it has errors, 2 on usage errors.
Types: `int`, `float`, `str`, `date` (ISO `YYYY-MM-DD`). Columns are required unless `"required": false`.

Run the tests with `python -m pytest`.
