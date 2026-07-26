import subprocess
import tempfile
import os
import uuid
import sys

DOCKER_IMAGE = "python:3.11-slim"
DEFAULT_TIMEOUT = 5  # seconds, hard limit for the whole docker run


def run_python_in_sandbox(code: str, stdin_input: str = "", timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Runs student Python code inside an isolated, network-disabled Docker container.
    Returns a dict with stdout, stderr, exit_code, timed_out, and error (if the sandbox itself failed)."""

    run_id = uuid.uuid4().hex[:8]
    tmp_dir = os.path.join(os.path.dirname(__file__), "sandbox_tmp", run_id)
    os.makedirs(tmp_dir, exist_ok=True)
    code_path = os.path.join(tmp_dir, "student_code.py")

    with open(code_path, "w", encoding="utf-8") as f:
        f.write(code)

    docker_cmd = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--memory", "128m",
        "--cpus", "0.5",
        "-v", f"{tmp_dir}:/sandbox:ro",
        "--workdir", "/sandbox",
        DOCKER_IMAGE,
        "python", "student_code.py",
    ]

    result = {
        "stdout": "",
        "stderr": "",
        "exit_code": None,
        "timed_out": False,
        "error": None,
    }

    creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0

    try:
        proc = subprocess.run(
            docker_cmd,
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=creation_flags,
        )
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
        result["exit_code"] = proc.returncode

    except subprocess.TimeoutExpired:
        result["timed_out"] = True
        result["error"] = f"Execution exceeded {timeout} second timeout."

    except FileNotFoundError:
        result["error"] = "Docker is not installed or not available on PATH."

    finally:
        try:
            os.remove(code_path)
            os.rmdir(tmp_dir)
        except OSError:
            pass  # best-effort cleanup

    return result


if __name__ == "__main__":
    print("=== Test 1: normal working code ===")
    code1 = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

print(bubble_sort([5, 2, 4, 1, 3]))
"""
    result1 = run_python_in_sandbox(code1)
    print(result1)

    print("\n=== Test 2: infinite loop (should time out) ===")
    code2 = """
while True:
    pass
"""
    result2 = run_python_in_sandbox(code2, timeout=3)
    print(result2)

    print("\n=== Test 3: code with a runtime error ===")
    code3 = """
print(1 / 0)
"""
    result3 = run_python_in_sandbox(code3)
    print(result3)