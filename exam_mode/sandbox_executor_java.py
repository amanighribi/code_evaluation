import subprocess
import os
import uuid
import sys
import re

DOCKER_IMAGE = "eclipse-temurin:17-jdk"
DEFAULT_TIMEOUT = 20  # seconds; covers compile + run, plus Docker cold start


def _extract_public_class_name(code: str) -> str:
    match = re.search(r"public\s+class\s+(\w+)", code)
    return match.group(1) if match else "Main"


def run_java_in_sandbox(code: str, stdin_input: str = "", timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Compiles and runs student Java code inside an isolated, network-disabled Docker container.
    Returns stdout, stderr, exit_code, timed_out, compile_error, and error (if the sandbox itself failed)."""

    class_name = _extract_public_class_name(code)
    run_id = uuid.uuid4().hex[:8]
    tmp_dir = os.path.join(os.path.dirname(__file__), "sandbox_tmp", run_id)
    os.makedirs(tmp_dir, exist_ok=True)
    code_path = os.path.join(tmp_dir, f"{class_name}.java")

    with open(code_path, "w", encoding="utf-8") as f:
        f.write(code)

    # Compile then run, inside the container, via a shell command.
    inner_cmd = f"javac {class_name}.java 2> compile_errors.txt && java {class_name}; echo COMPILE_STATUS:$?"

    docker_cmd = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--memory", "256m",
        "--cpus", "0.5",
        "-v", f"{tmp_dir}:/sandbox",
        "--workdir", "/sandbox",
        DOCKER_IMAGE,
        "sh", "-c", inner_cmd,
    ]

    result = {
        "stdout": "",
        "stderr": "",
        "exit_code": None,
        "timed_out": False,
        "compile_error": None,
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
        raw_stdout = proc.stdout
        if "COMPILE_STATUS:" in raw_stdout:
            raw_stdout = raw_stdout.split("COMPILE_STATUS:")[0]
        result["stdout"] = raw_stdout
        result["stderr"] = proc.stderr
        result["exit_code"] = proc.returncode

        compile_errors_path = os.path.join(tmp_dir, "compile_errors.txt")
        if os.path.exists(compile_errors_path):
            with open(compile_errors_path, "r", encoding="utf-8", errors="replace") as f:
                compile_err_text = f.read().strip()
            if compile_err_text:
                result["compile_error"] = compile_err_text

    except subprocess.TimeoutExpired:
        result["timed_out"] = True
        result["error"] = f"Execution exceeded {timeout} second timeout."

    except FileNotFoundError:
        result["error"] = "Docker is not installed or not available on PATH."

    finally:
        try:
            for fname in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, fname))
            os.rmdir(tmp_dir)
        except OSError:
            pass  # best-effort cleanup

    return result


if __name__ == "__main__":
    print("=== Test 1: working code ===")
    code1 = """
public class Sorter {
    public static void main(String[] args) {
        int[] arr = {5, 2, 4, 1, 3};
        for (int i = 0; i < arr.length; i++) {
            for (int j = 0; j < arr.length - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
        for (int x : arr) {
            System.out.print(x + " ");
        }
    }
}
"""
    print(run_java_in_sandbox(code1))

    print("\n=== Test 2: compile error ===")
    code2 = """
public class Broken {
    public static void main(String[] args) {
        int x = ;
    }
}
"""
    print(run_java_in_sandbox(code2))

    print("\n=== Test 3: infinite loop (should time out) ===")
    code3 = """
public class Infinite {
    public static void main(String[] args) {
        while (true) {}
    }
}
"""
    print(run_java_in_sandbox(code3, timeout=8))