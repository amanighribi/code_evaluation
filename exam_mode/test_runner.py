from exam_mode.sandbox_executor import run_python_in_sandbox
from exam_mode.sandbox_executor_java import run_java_in_sandbox


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
        passed = (
            actual == expected
            and not exec_result["timed_out"]
            and exec_result["exit_code"] == 0
            and not compile_error
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