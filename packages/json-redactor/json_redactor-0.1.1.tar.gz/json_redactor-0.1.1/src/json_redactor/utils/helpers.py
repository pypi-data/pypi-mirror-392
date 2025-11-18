import hashlib
import json
from pathlib import Path
from re import Pattern
import re
from typing import Any, Iterable, List, Optional, Set, TextIO, Tuple

import ijson
import typer

from json_redactor.settings import get_settings
from json_redactor.utils import RedactionMode
from json_redactor.utils.hash_executor import HashExecutor


settings = get_settings()


def is_sensitive(key: str, exact_keys: Set[str], regex_list: List[Pattern]) -> bool:
    """
    Check if a key matches:
      - an exact case-insensitive key
      - or any regex pattern
    """
    key_lower = key.lower()

    if key_lower in exact_keys:
        return True

    for pattern in regex_list:
        if pattern.search(key):
            return True

    return False


def hash_value(value: Any) -> str:
    """
    Deterministically hash a JSON value using SHA-256.

    Strings are hashed directly; non-strings are first canonicalised via json.dumps
    to ensure deterministic representation.
    """
    if isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")

    digest = hashlib.sha256(payload).hexdigest()
    return digest


def redact_value(value: Any, mode: RedactionMode) -> Any:
    """
    Apply redaction to a value according to the chosen mode.
    """
    if mode == RedactionMode.MASK:
        return settings.SENSITIVE_MASK
    elif mode == RedactionMode.HASH:
        return hash_value(value)
    else:
        # Defensive: should never happen because mode is an Enum.
        return settings.SENSITIVE_MASK


def stream_redact_json(
    in_stream: TextIO,
    out_stream: TextIO,
    sensitive_keys: Set[str],
    sensitive_regex: List[Pattern],
    mode: RedactionMode,
) -> None:
    """
    Stream over JSON from `in_stream`, redacting sensitive values and writing to `out_stream`.

    Uses `ijson.basic_parse` to avoid loading the whole JSON document into memory.
    Preserves structure and key order; formatting/whitespace may differ from the input.
    """

    # Stack frames track whether we're in an array or an object, and whether
    # we've already written any elements (for comma management).
    class Frame:
        __slots__ = ("kind", "first")

        def __init__(self, kind: str) -> None:
            self.kind = kind  # "map" or "array"
            self.first = True

    stack: list[Frame] = []
    pending_key: Optional[str] = None
    hash_exec = HashExecutor(max_workers=4) if mode == RedactionMode.HASH else None
    pending_futures = {}

    # Helper for writing comma before a new element when needed.
    def before_new_element() -> None:
        if stack:
            frame = stack[-1]
            if not frame.first:
                out_stream.write(",")
            frame.first = False

    events: Iterable[Tuple[str, Any]] = ijson.basic_parse(in_stream)

    try:
        for event, value in events:
            if event == "start_map":
                if stack and stack[-1].kind == "array":
                    # Starting an object — it may itself be an element in an array or value of a key.
                    before_new_element()
                out_stream.write("{")
                stack.append(Frame("map"))

            elif event == "end_map":
                out_stream.write("}")
                stack.pop()

            elif event == "start_array":
                if stack and stack[-1].kind == "array":
                    # Starting an array.
                    before_new_element()
                out_stream.write("[")
                stack.append(Frame("array"))

            elif event == "end_array":
                out_stream.write("]")
                stack.pop()

            elif event == "map_key":
                # A key inside an object.
                frame = stack[-1]
                if not frame.first:
                    out_stream.write(",")
                frame.first = False

                pending_key = value
                out_stream.write(
                    json.dumps(value, ensure_ascii=False, default=str)
                )  # if decimal exists in JSON
                out_stream.write(":")

            elif event in ("string", "number", "boolean", "null"):
                if stack and stack[-1].kind == "array":
                    before_new_element()

                actual_value = None if event == "null" else value

                if pending_key is not None:
                    key = pending_key
                    pending_key = None

                    if is_sensitive(key, sensitive_keys, sensitive_regex):
                        if mode == RedactionMode.MASK:
                            actual_value = "***REDACTED***"
                        else:
                            future = hash_exec.submit(actual_value)
                            pending_futures[id(future)] = future
                            actual_value = future.result()

                out_stream.write(
                    json.dumps(
                        actual_value,
                        ensure_ascii=False,
                        default=str,
                    )
                )
    finally:
        if hash_exec:
            hash_exec.shutdown()

    out_stream.write("\n")


def load_sensitive_keys(
    keys_option: Optional[str],
    key_file: Optional[Path],
    keys_regex_option: Optional[str] = None,
) -> Set[str]:
    """
    Build a case-insensitive set of sensitive keys from:
      - a comma-separated list
      - and/or a file with one key per line.
    """
    sensitive: Set[str] = set()
    regex_patterns: List[Pattern] = []

    if keys_option:
        for raw in keys_option.split(","):
            key = raw.strip()
            if key:
                sensitive.add(key.lower())

    if key_file:
        if not key_file.exists():
            typer.echo(f"Error: key file not found: {key_file}", err=True)
            raise typer.Exit(code=1)
        try:
            with key_file.open("r", encoding="utf-8") as f:
                for line in f:
                    key = line.strip()
                    if key:
                        sensitive.add(key.lower())
        except OSError as exc:
            typer.echo(f"Error reading key file: {exc}", err=True)
            raise typer.Exit(code=1)

    if keys_regex_option:
        for raw in keys_regex_option.split(","):
            pattern = raw.strip()
            if pattern:
                try:
                    regex_patterns.append(re.compile(pattern, re.IGNORECASE))
                except re.error as exc:
                    raise ValueError(f"Invalid regex '{pattern}': {exc}")

    return sensitive, regex_patterns
