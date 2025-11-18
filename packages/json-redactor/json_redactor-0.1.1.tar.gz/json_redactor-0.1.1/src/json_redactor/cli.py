from __future__ import annotations


import sys
from pathlib import Path
from typing import Optional

import typer

from json_redactor.utils import RedactionMode
from json_redactor.utils.helpers import load_sensitive_keys, stream_redact_json


app = typer.Typer(add_completion=False)


SENSITIVE_MASK = "***REDACTED***"


@app.command()
def main(
    input_path: Optional[Path] = typer.Argument(
        None,
        help=(
            "Path to input JSON file. If omitted, reads from stdin. "
            "Use '-' explicitly to force stdin."
        ),
    ),
    keys: Optional[str] = typer.Option(
        None,
        "--keys",
        help="Comma-separated list of sensitive keys (case-insensitive), e.g. 'email,password,ssn'.",
    ),
    key_file: Optional[Path] = typer.Option(
        None,
        "--key-file",
        help="Path to a text file containing one sensitive key per line.",
    ),
    keys_regex: Optional[str] = typer.Option(
        None,
        "--keys-regex",
        help="Comma-separated regex patterns for sensitive keys (case-insensitive). Example: '(?i)email,pass(word)?'.",
    ),
    mask: bool = typer.Option(
        False,
        "--mask",
        help="Redact sensitive values by replacing them with a fixed mask (***REDACTED***). Default if neither flag is set.",
    ),
    hash_: bool = typer.Option(
        False,
        "--hash",
        help="Redact sensitive values by replacing them with a deterministic SHA-256 hash.",
    ),
) -> None:
    """
    Redact or hash sensitive data in a JSON document while preserving structure and key order.

    Example:
        cat people.json | json-redactor --keys email,ssn --hash > output.json
    """

    # Determine redaction mode from flags.
    if mask and hash_:
        typer.echo("Error: --mask and --hash are mutually exclusive.", err=True)
        raise typer.Exit(code=1)

    if hash_:
        mode = RedactionMode.HASH
    else:
        mode = RedactionMode.MASK

    sensitive_keys, sensitive_regex = load_sensitive_keys(keys, key_file, keys_regex)

    if not sensitive_keys and not sensitive_regex:
        typer.echo(
            "Warning: no sensitive keys specified; output will be identical to input.",
            err=True,
        )

    if input_path is None or str(input_path) == "-":
        in_stream = sys.stdin

    else:
        if not input_path.exists():
            typer.echo(f"Error: input file not found: {input_path}", err=True)
            raise typer.Exit(code=1)

        try:
            in_stream = input_path.open("r", encoding="utf-8")
        except OSError as exc:
            typer.echo(f"Error opening input file: {exc}", err=True)
            raise typer.Exit(code=1)

    try:
        stream_redact_json(
            in_stream=in_stream,
            out_stream=sys.stdout,
            sensitive_keys=sensitive_keys,
            sensitive_regex=sensitive_regex,
            mode=mode,
        )
    finally:
        if input_path and str(input_path) != "-":
            in_stream.close()


if __name__ == "__main__":
    app()

def cli(): # for building it as a package entry point
    app()