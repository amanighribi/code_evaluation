import re
from exam_mode.sandbox_executor import run_python_in_sandbox
from exam_mode.sandbox_executor_java import run_java_in_sandbox


def normalize_output(text: str) -> str:
    """Collapses runs of whitespace into single spaces and strips leading/trailing
    whitespace, so trivial formatting differences (extra spaces, mixed line breaks)
    don't cause a genuinely correct answer to be marked as failed. Does NOT change
    the actual content/characters, only whitespace layout."""
    return re.sub(r"\s+", " ", text).strip()


def run_test_cases(code: str, test_cases: list, language: str = "python", timeout: int = 20) -> list:
    """test_cases: list of {"input": "...", "expected_output": "..."}
    Runs the student's code once per test case, feeding stdin and comparing stdout.
    Returns a list of result dicts."""

    results = []

    for i, case in enumerate(test_cases, start=1):
        test_input = case.get("input", "")
        expected = case.get("expected_output", "").strip()

        if language == "python":
            exec_result = run_python_in_sandbox(code, stdin_input=test_input, timeout=timeout)
            compile_error = None
        elif language == "java":
            exec_result = run_java_in_sandbox(code, stdin_input=test_input, timeout=timeout)
            compile_error = exec_result.get("compile_error")
        else:
            raise ValueError(f"Unsupported language: {language}")

        actual = exec_result["stdout"].strip()
        infra_error = exec_result.get("error")

        outputs_match = normalize_output(actual) == normalize_output(expected)

        passed = (
            outputs_match
            and not exec_result["timed_out"]
            and exec_result["exit_code"] == 0
            and not compile_error
            and not infra_error
        )

        results.append({
            "test_number": i,
            "input": test_input,
            "expected_output": expected,
            "actual_output": actual,
            "passed": passed,
            "timed_out": exec_result["timed_out"],
            "exit_code": exec_result["exit_code"],
            "stderr": exec_result["stderr"],
            "compile_error": compile_error,
            "infra_error": infra_error,
        })

    return results


def summarize_results(results: list) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 2) if total else 0,
    }

from exam_mode.sandbox_executor import run_python_project_in_sandbox


from exam_mode.sandbox_executor import run_python_project_in_sandbox
from exam_mode.sandbox_executor_java import run_java_project_in_sandbox


def run_test_cases_project(project_dir: str, entry_point: str, test_cases: list, language: str = "python", timeout: int = 20) -> list:
    """Same as run_test_cases, but runs a multi-file project with a specified entry point
    instead of a single inline code string. Supports both Python and Java."""

    results = []

    for i, case in enumerate(test_cases, start=1):
        test_input = case.get("input", "")
        expected = case.get("expected_output", "").strip()

        if language == "python":
            exec_result = run_python_project_in_sandbox(project_dir, entry_point, stdin_input=test_input, timeout=timeout)
            compile_error = None
        elif language == "java":
            exec_result = run_java_project_in_sandbox(project_dir, entry_point, stdin_input=test_input, timeout=timeout)
            compile_error = exec_result.get("compile_error")
        else:
            raise ValueError(f"Unsupported language: {language}")

        actual = exec_result["stdout"].strip()
        infra_error = exec_result.get("error")
        outputs_match = normalize_output(actual) == normalize_output(expected)

        passed = (
            outputs_match
            and not exec_result["timed_out"]
            and exec_result["exit_code"] == 0
            and not compile_error
            and not infra_error
        )

        results.append({
            "test_number": i,
            "input": test_input,
            "expected_output": expected,
            "actual_output": actual,
            "passed": passed,
            "timed_out": exec_result["timed_out"],
            "exit_code": exec_result["exit_code"],
            "stderr": exec_result["stderr"],
            "compile_error": compile_error,
            "infra_error": infra_error,
        })

    return results