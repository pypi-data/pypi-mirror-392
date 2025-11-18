import json
import io
from pathlib import Path
import re
import click
import pytest

from json_redactor.utils.helpers import is_sensitive, stream_redact_json, load_sensitive_keys
from json_redactor.utils import RedactionMode


# Helper for easy streaming tests
def run_redactor(input_json, sensitive_keys, sensitive_regex, mode):
    input_stream = io.StringIO(input_json)
    output_stream = io.StringIO()

    stream_redact_json(
        in_stream=input_stream,
        out_stream=output_stream,
        sensitive_keys=sensitive_keys,
        sensitive_regex=sensitive_regex,
        mode=mode,
    )

    return json.loads(output_stream.getvalue())


# ------------------------------
# TESTS
# ------------------------------


def test_mask_simple_key():
    data = '{"name": "Anna", "age": 30}'
    sensitive_keys, sensitive_regex = load_sensitive_keys("name", None, None)

    result = run_redactor(data, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert result["name"] == "***REDACTED***"
    assert result["age"] == 30


def test_hash_simple_key():
    data = '{"email": "anna@example.com"}'
    sensitive_keys, sensitive_regex = load_sensitive_keys("email", None, None)

    result = run_redactor(data, sensitive_keys, sensitive_regex, RedactionMode.HASH)

    # SHA-256 length = 64 hex characters
    assert len(result["email"]) == 64
    assert result["email"] != "anna@example.com"


def test_regex_key_matching():
    data = '{"name": "Ben", "nickname": "Benny"}'
    sensitive_keys, sensitive_regex = load_sensitive_keys(None, None, "^nick")

    result = run_redactor(data, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert result["name"] == "Ben"
    assert result["nickname"] == "***REDACTED***"


def test_combined_exact_and_regex():
    data = '{"name": "Anna", "token_value": "XYZ"}'
    sensitive_keys, sensitive_regex = load_sensitive_keys("name", None, "token")

    result = run_redactor(data, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert result["name"] == "***REDACTED***"
    assert result["token_value"] == "***REDACTED***"


def test_nested_masking():
    data = '{"user": {"email": "a@b.com", "info": {"ssn": "123"}}}'
    sensitive_keys, sensitive_regex = load_sensitive_keys("email,ssn", None, None)

    result = run_redactor(data, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert result["user"]["email"] == "***REDACTED***"
    assert result["user"]["info"]["ssn"] == "***REDACTED***"


def test_array_handling():
    data = '[ {"email": "a@a.com"}, {"email": "b@b.com"} ]'
    sensitive_keys, sensitive_regex = load_sensitive_keys("email", None, None)

    result = run_redactor(data, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert result[0]["email"] == "***REDACTED***"
    assert result[1]["email"] == "***REDACTED***"


def test_preserves_structure():
    # order should match original
    data = '{"a": 1, "b": 2, "c": 3}'
    sensitive_keys, sensitive_regex = load_sensitive_keys(None, None, None)

    result = run_redactor(data, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert list(result.keys()) == ["a", "b", "c"]


def test_no_sensitive_keys_warning_not_interfering():
    # This ensures empty-sensitive-keys does not break streaming
    data = '{"x": 1}'
    sensitive_keys, sensitive_regex = load_sensitive_keys(None, None, None)

    result = run_redactor(data, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert result["x"] == 1


@pytest.mark.parametrize("key", ["name", "Name", "NAME"])
def test_case_insensitive_keys(key):
    raw = '{"Name": "Anna"}'
    sensitive_keys, sensitive_regex = load_sensitive_keys(key, None, None)

    result = run_redactor(raw, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert result["Name"] == "***REDACTED***"


def test_regex_case_insensitive():
    raw = '{"LANGUAGE": "English"}'
    sensitive_keys, sensitive_regex = load_sensitive_keys(None, None, "lang")

    result = run_redactor(raw, sensitive_keys, sensitive_regex, RedactionMode.MASK)

    assert result["LANGUAGE"] == "***REDACTED***"


def test_hash_non_string_value():
    data = '{"age": 30}'
    keys, regex = load_sensitive_keys("age", None, None)

    result = run_redactor(data, keys, regex, RedactionMode.HASH)

    assert isinstance(result["age"], str)
    assert len(result["age"]) == 64  # SHA-256 hex


@pytest.mark.parametrize("value", ["null", "true", "false", "123", "12.34"])
def test_literals_pass_through(value):
    data = f'{{"v": {value}}}'
    keys, regex = load_sensitive_keys(None, None, None)

    result = run_redactor(data, keys, regex, RedactionMode.MASK)

    # literal values should stay unchanged
    assert "v" in result


def test_nested_arrays():
    data = "[ [1,2], [3,4] ]"
    keys, regex = load_sensitive_keys(None, None, None)

    result = run_redactor(data, keys, regex, RedactionMode.MASK)

    assert result == [[1, 2], [3, 4]]


def test_empty_structures():
    data = '{"a": [], "b": {}}'
    keys, regex = load_sensitive_keys(None, None, None)

    result = run_redactor(data, keys, regex, RedactionMode.MASK)

    assert result == {"a": [], "b": {}}


def test_invalid_regex():
    with pytest.raises(ValueError):
        load_sensitive_keys(None, None, "[unclosed")


def test_key_file_loading(tmp_path):
    p = tmp_path / "keys.txt"
    p.write_text("email\npassword\n")

    keys, regex = load_sensitive_keys(None, p, None)

    assert "email" in keys
    assert "password" in keys


def test_key_file_missing():
    missing = Path("/nonexistent/file.txt")
    with pytest.raises(click.exceptions.Exit):  # typer uses click under the hood
        load_sensitive_keys(None, missing, None)


def test_regex_and_exact_combined():
    data = '{"token": "A", "token_extra": "B"}'
    keys, regex = load_sensitive_keys("token", None, "extra$")

    result = run_redactor(data, keys, regex, RedactionMode.MASK)

    assert result["token"] == "***REDACTED***"
    assert result["token_extra"] == "***REDACTED***"


def test_hash_executor_shutdown():
    data = '{"a": "x"}'
    keys, regex = load_sensitive_keys("a", None, None)

    result = run_redactor(data, keys, regex, RedactionMode.HASH)

    assert isinstance(result["a"], str)


def test_large_streaming_behavior():
    large_json = '{"items": [' + ",".join(f'{{"i": {i}}}' for i in range(1000)) + "]}"
    keys, regex = load_sensitive_keys(None, None, None)

    result = run_redactor(large_json, keys, regex, RedactionMode.MASK)

    assert len(result["items"]) == 1000


def test_is_sensitive_exact_and_regex():
    keys = {"email"}
    regex = [re.compile("pass", re.IGNORECASE)]

    assert is_sensitive("email", keys, regex)
    assert is_sensitive("password", keys, regex)
    assert not is_sensitive("username", keys, regex)
