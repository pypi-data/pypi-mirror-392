import pytest
import subprocess
import sys
import json
from toon import encode, decode

def run_cli(args, input_data=None):
    cmd = [sys.executable, "-m", "toon.cli"] + args
    result = subprocess.run(
        cmd,
        input=input_data,
        text=True,
        capture_output=True
    )
    return result.returncode, result.stdout, result.stderr

def test_cli_encode_basic():
    input_data = '{"name": "Alice", "age": 30}'
    code, stdout, stderr = run_cli(["encode"], input_data=input_data)
    assert code == 0
    assert "name: Alice" in stdout
    assert "age: 30" in stdout

def test_cli_decode_basic():
    input_data = "name: Alice\nage: 30"
    code, stdout, stderr = run_cli(["decode"], input_data=input_data)
    assert code == 0
    data = json.loads(stdout)
    assert data["name"] == "Alice"
    assert data["age"] == 30

def test_cli_encode_tab_delimiter():
    input_data = '{"items": [{"id": 1, "name": "Test"}]}'
    code, stdout, stderr = run_cli(["encode", "--delimiter", "tab"], input_data=input_data)
    assert code == 0
    assert "\t" in stdout or "items" in stdout

def test_cli_decode_pretty():
    input_data = "name: Alice\nage: 30"
    code, stdout, stderr = run_cli(["decode", "--pretty"], input_data=input_data)
    assert code == 0
    assert "  " in stdout
    data = json.loads(stdout)
    assert data["name"] == "Alice"

def test_cli_encode_empty_input():
    code, stdout, stderr = run_cli(["encode"], input_data="")
    assert code == 1
    assert "No input data" in stderr

def test_cli_decode_empty_input():
    code, stdout, stderr = run_cli(["decode"], input_data="")
    assert code == 1
    assert "No input data" in stderr

def test_cli_encode_invalid_json():
    code, stdout, stderr = run_cli(["encode"], input_data="invalid json")
    assert code == 1
    assert "Invalid JSON" in stderr

def test_cli_help():
    code, stdout, stderr = run_cli(["--help"])
    assert code == 0
    assert "TOON" in stdout
    assert "encode" in stdout
    assert "decode" in stdout

