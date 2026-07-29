import pytest
from exam_mode.sandbox_executor import run_python_in_sandbox


@pytest.mark.docker
def test_runs_simple_code_successfully():
    code = "print('hello')\n"
    result = run_python_in_sandbox(code, timeout=15)
    assert result["stdout"].strip() == "hello"
    assert result["exit_code"] == 0
    assert not result["timed_out"]


@pytest.mark.docker
def test_captures_stdin_input():
    code = "x = input()\nprint(x.upper())\n"
    result = run_python_in_sandbox(code, stdin_input="hello\n", timeout=15)
    assert result["stdout"].strip() == "HELLO"


@pytest.mark.docker
def test_captures_runtime_error():
    code = "print(1 / 0)\n"
    result = run_python_in_sandbox(code, timeout=15)
    assert result["exit_code"] != 0
    assert "ZeroDivisionError" in result["stderr"]


@pytest.mark.docker
def test_infinite_loop_times_out():
    code = "while True:\n    pass\n"
    result = run_python_in_sandbox(code, timeout=5)
    assert result["timed_out"] is True


@pytest.mark.docker
def test_network_access_is_blocked():
    code = """
import urllib.request
try:
    urllib.request.urlopen('http://example.com', timeout=3)
    print("NETWORK_ACCESSIBLE")
except Exception as e:
    print("NETWORK_BLOCKED")
"""
    result = run_python_in_sandbox(code, timeout=15)
    assert "NETWORK_BLOCKED" in result["stdout"]