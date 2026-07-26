from exam_mode.sandbox_executor import run_python_in_sandbox


def run_test_cases(code: str, test_cases: list, timeout: int = 20) -> list:
    """test_cases: list of {"input": "...", "expected_output": "..."}
    Runs the student's code once per test case, feeding stdin and comparing stdout.
    Returns a list of result dicts."""

    results = []

    for i, case in enumerate(test_cases, start=1):
        test_input = case.get("input", "")
        expected = case.get("expected_output", "").strip()

        exec_result = run_python_in_sandbox(code, stdin_input=test_input, timeout=timeout)

        actual = exec_result["stdout"].strip()
        passed = (actual == expected) and not exec_result["timed_out"] and exec_result["exit_code"] == 0

        results.append({
            "test_number": i,
            "input": test_input,
            "expected_output": expected,
            "actual_output": actual,
            "passed": passed,
            "timed_out": exec_result["timed_out"],
            "exit_code": exec_result["exit_code"],
            "stderr": exec_result["stderr"],
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


if __name__ == "__main__":
    student_code = """
n = int(input())
arr = list(map(int, input().split()))

for i in range(n):
    for j in range(0, n - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]

print(' '.join(map(str, arr)))
"""

    test_cases = [
        {"input": "5\n5 2 4 1 3", "expected_output": "1 2 3 4 5"},
        {"input": "3\n3 2 1", "expected_output": "1 2 3"},
        {"input": "1\n42", "expected_output": "42"},
        {"input": "4\n1 1 1 1", "expected_output": "1 1 1 1"},
    ]

    print("Running test cases...\n")
    results = run_test_cases(student_code, test_cases)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"Test {r['test_number']}: {status}")
        print(f"  Input: {r['input']!r}")
        print(f"  Expected: {r['expected_output']!r}")
        print(f"  Actual:   {r['actual_output']!r}")
        if r["stderr"]:
            print(f"  Stderr: {r['stderr'][:200]}")
        print()

    summary = summarize_results(results)
    print(f"Summary: {summary['passed']}/{summary['total']} passed ({summary['pass_rate']*100:.0f}%)")