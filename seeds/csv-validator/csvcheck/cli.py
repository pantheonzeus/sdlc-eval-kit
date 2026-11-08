"""Command line: python -m csvcheck FILE --schema SCHEMA."""

import argparse
import sys

from csvcheck.schema import Schema, SchemaError
from csvcheck.validate import validate_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="csvcheck", description="Validate a CSV file against a schema.")
    parser.add_argument("file", help="CSV file with a header row")
    parser.add_argument("--schema", required=True, help="JSON schema file")
    args = parser.parse_args(argv)
    try:
        schema = Schema.load(args.schema)
    except (OSError, SchemaError, ValueError) as exc:
        print(f"schema error: {exc}", file=sys.stderr)
        return 2
    try:
        errors = validate_file(args.file, schema)
    except OSError as exc:
        print(f"cannot read {args.file}: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(error)
    return 1 if errors else 0
