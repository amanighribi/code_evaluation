import json
from exam_mode.extract_constraints import extract_banned_names
from exam_mode.constraint_checker import check_constraints_multilang
from exam_mode.test_runner import run_test_cases, summarize_results
from exam_mode.evaluate_submission import evaluate_submission


def run_full_exam_evaluation(instructions: str, student_code: str, test_cases: list = None, language: str = "python") -> dict:
    print("Step 1: Extracting constraints from instructions...")
    banned_names = extract_banned_names(instructions)
    print(f"  Banned: {banned_names}")

    print("Step 2: Checking constraint violations...")
    violations = check_constraints_multilang(student_code, banned_names, language=language)
    print(f"  Found {len(violations)} violation(s)")

    test_results = []
    if test_cases:
        print("Step 3: Running test cases in sandbox...")
        test_results = run_test_cases(student_code, test_cases)
        summary = summarize_results(test_results)
        print(f"  {summary['passed']}/{summary['total']} passed")
    else:
        print("Step 3: No test cases provided, skipping execution.")

    print("Step 4: Generating holistic evaluation...")
    evaluation = evaluate_submission(instructions, student_code, violations, test_results)

    return {
        "banned_names": banned_names,
        "constraint_violations": violations,
        "test_results": test_results,
        "evaluation": evaluation,
    }


if __name__ == "__main__":
    instructions = """
    Écrivez un programme qui lit un entier n, puis une liste de n entiers,
    et affiche la liste triée par ordre croissant en utilisant l'algorithme du tri à bulles.
    N'utilisez pas sort() ou sorted().
    """

    lazy_code = """
n = int(input())
arr = list(map(int, input().split()))
arr.sort()
print(' '.join(map(str, arr)))
"""

    test_cases = [
        {"input": "5\n5 2 4 1 3", "expected_output": "1 2 3 4 5"},
        {"input": "3\n3 2 1", "expected_output": "1 2 3"},
    ]

    result = run_full_exam_evaluation(instructions, lazy_code, test_cases, language="python")

    print("\n" + "=" * 70)
    print("FULL EXAM EVALUATION REPORT")
    print("=" * 70)
    print(json.dumps(result, indent=2, ensure_ascii=False))