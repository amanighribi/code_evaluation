import json
import os
from project_utils.zip_extractor import find_code_files
from exam_mode.extract_constraints import extract_exam_metadata
from exam_mode.constraint_checker import check_constraints_multilang
from exam_mode.test_runner import run_test_cases, summarize_results
from exam_mode.evaluate_submission import evaluate_submission


def run_full_exam_evaluation(instructions: str, student_code: str, language: str = "python") -> dict:
    print("Step 1: Extracting constraints and test cases from instructions...")
    metadata = extract_exam_metadata(instructions)
    banned_names = metadata["banned_names"]
    test_cases = metadata["test_cases"]
    print(f"  Banned: {banned_names}")
    print(f"  Test cases extracted: {len(test_cases)}")

    print("Step 2: Checking constraint violations...")
    violations = check_constraints_multilang(student_code, banned_names, language=language)
    print(f"  Found {len(violations)} violation(s)")

    test_results = []
    if test_cases:
        print("Step 3: Running test cases in sandbox...")
        test_results = run_test_cases(student_code, test_cases, language=language)
        summary = summarize_results(test_results)
        print(f"  {summary['passed']}/{summary['total']} passed")
    else:
        print("Step 3: No test cases found in instructions, skipping execution.")

    print("Step 4: Generating holistic evaluation...")
    evaluation = evaluate_submission(instructions, student_code, violations, test_results)

    return {
        "banned_names": banned_names,
        "extracted_test_cases": test_cases,
        "constraint_violations": violations,
        "test_results": test_results,
        "evaluation": evaluation,
    }


if __name__ == "__main__":
    instructions = """
    Écrivez un programme qui lit un entier n, puis une liste de n entiers,
    et affiche la liste triée par ordre croissant en utilisant l'algorithme du tri à bulles.
    N'utilisez pas sort() ou sorted().

    Par exemple, pour n=5 et la liste [5, 2, 4, 1, 3], la sortie devrait être :
    1 2 3 4 5
    """

    lazy_code = """
n = int(input())
arr = list(map(int, input().split()))
arr.sort()
print(' '.join(map(str, arr)))
"""

    result = run_full_exam_evaluation(instructions, lazy_code, language="python")

    print("\n" + "=" * 70)
    print("FULL EXAM EVALUATION REPORT")
    print("=" * 70)
    print(json.dumps(result, indent=2, ensure_ascii=False))

from exam_mode.constraint_checker import check_constraints_project
from exam_mode.test_runner import run_test_cases_project
from exam_mode.entry_point_resolver import resolve_entry_point, EntryPointError


def run_full_exam_evaluation_project(instructions: str, project_dir: str, language: str = "python", requested_entry_point: str = None) -> dict:
    print("Resolving entry point...")
    try:
        entry_point = resolve_entry_point(project_dir, language, requested_entry_point)
    except EntryPointError as e:
        return {"error": str(e)}
    print(f"  Entry point: {entry_point}")

    print("Step 1: Extracting constraints and test cases from instructions...")
    metadata = extract_exam_metadata(instructions)
    banned_names = metadata["banned_names"]
    test_cases = metadata["test_cases"]
    print(f"  Banned: {banned_names}")
    print(f"  Test cases extracted: {len(test_cases)}")

    print("Step 2: Checking constraint violations across all project files...")
    violations = check_constraints_project(project_dir, banned_names, language=language)
    print(f"  Found {len(violations)} violation(s)")

    test_results = []
    if test_cases:
        print("Step 3: Running test cases in sandbox...")
        test_results = run_test_cases_project(project_dir, entry_point, test_cases, language=language)
        summary = summarize_results(test_results)
        print(f"  {summary['passed']}/{summary['total']} passed")
    else:
        print("Step 3: No test cases found in instructions, skipping execution.")

    # Read entry point + all files for evaluation context
    all_code_files = find_code_files(project_dir, ".py" if language == "python" else ".java")
    combined_source = ""
    for rel_path in all_code_files:
        full_path = os.path.join(project_dir, rel_path)
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            combined_source += f"\n--- {rel_path} ---\n" + f.read()

    print("Step 4: Generating holistic evaluation...")
    evaluation = evaluate_submission(instructions, combined_source, violations, test_results)

    return {
        "entry_point": entry_point,
        "banned_names": banned_names,
        "extracted_test_cases": test_cases,
        "constraint_violations": violations,
        "test_results": test_results,
        "evaluation": evaluation,
    }