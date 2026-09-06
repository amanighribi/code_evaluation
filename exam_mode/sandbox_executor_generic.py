import subprocess
import os
import uuid
import sys
from exam_mode.language_config import get_language_config

DEFAULT_TIMEOUT = 25  # generous; covers image pull/cold-start + compile + run


def run_generic_in_sandbox(code: str, language: str, stdin_input: str = "", timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Compiles (if needed) and runs code in any language listed in LANGUAGE_CONFIG,
    inside an isolated, network-disabled Docker container. Same safety guarantees
    as the Python/Java executors: no network, bounded memory/CPU, hard timeout."""

    config = get_language_config(language)
    result = {
        "stdout": "", "stderr": "", "exit_code": None, "timed_out": False,
        "compile_error": None, "error": None,
    }

    if not config:
        result["error"] = f"No sandbox configuration found for language: {language}"
        return result

    run_id = uuid.uuid4().hex[:8]
    tmp_dir = os.path.join(os.path.dirname(__file__), "sandbox_tmp", run_id)
    os.makedirs(tmp_dir, exist_ok=True)
    code_path = os.path.join(tmp_dir, config["filename"])

    with open(code_path, "w", encoding="utf-8") as f:
        f.write(code)

    if config["compile_cmd"]:
        inner_cmd = f"{config['compile_cmd']} && {config['run_cmd']}; echo COMPILE_STATUS:$?"
    else:
        inner_cmd = f"{config['run_cmd']}; echo COMPILE_STATUS:$?"

    docker_cmd = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--memory", "256m",
        "--cpus", "0.5",
        "-v", f"{tmp_dir}:/sandbox",
        "--workdir", "/sandbox",
        config["image"],
        "sh", "-c", inner_cmd,
    ]

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
            pass

    return result


if __name__ == "__main__":
    print("=== Test: JavaScript ===")
    js_code = 'console.log("hello from js");'
    print(run_generic_in_sandbox(js_code, "javascript", timeout=30))

    print("\n=== Test: C ===")
    c_code = '#include <stdio.h>\nint main() { printf("hello from c\\n"); return 0; }'
    print(run_generic_in_sandbox(c_code, "c", timeout=30))