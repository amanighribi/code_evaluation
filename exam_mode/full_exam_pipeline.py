import json
import os

from project_utils.zip_extractor import find_code_files
from exam_mode.extract_constraints import extract_exam_metadata
from exam_mode.constraint_checker import check_constraints_multilang, check_constraints_project
from exam_mode.test_runner import run_test_cases, run_test_cases_project, summarize_results
from exam_mode.evaluate_submission import evaluate_submission
from exam_mode.language_config import LANGUAGE_CONFIG
from exam_mode.entry_point_resolver import resolve_project, list_source_files, EntryPointError
from exam_mode.java_static_checks import run_static_checks, build_evaluation_evidence

MAX_CONTEXT_CHARS = 80_000        # keeps a large Spring project inside the model's context
MAX_CHARS_PER_FILE = 15_000


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
        **build_evaluation_evidence(None, test_results, metadata["extraction_status"]),
        "evaluation": evaluation,
    }


def _build_review_context(project_dir: str, language: str) -> str:
    """Source shown to the LLM: no build output, IDE files or tests; capped so big projects still fit."""
    parts, total = [], 0
    for rel_path in list_source_files(project_dir, language):
        with open(os.path.join(project_dir, rel_path), "r", encoding="utf-8", errors="replace") as f:
            body = f.read()
        if len(body) > MAX_CHARS_PER_FILE:
            body = body[:MAX_CHARS_PER_FILE] + "\n... [truncated]"
        chunk = f"\n--- {rel_path.replace(chr(92), '/')} ---\n{body}"
        if total + len(chunk) > MAX_CONTEXT_CHARS:
            parts.append("\n... [remaining files omitted: context limit]")
            break
        parts.append(chunk)
        total += len(chunk)
    return "".join(parts)


def run_full_exam_evaluation_project(instructions: str, project_dir: str, language: str = "python", requested_entry_point: str = None) -> dict:
    print("Resolving language and entry point...")
    try:
        language, entry_point = resolve_project(project_dir, language, requested_entry_point)
    except EntryPointError as e:
        return {"error": str(e)}
    print(f"  Language: {language} | Entry point: {entry_point}")

    print("Step 1: Extracting constraints and test cases from instructions...")
    metadata = extract_exam_metadata(instructions)
    banned_names = metadata["banned_names"]
    test_cases = metadata["test_cases"]
    print(f"  Banned: {banned_names}")
    print(f"  Test cases extracted: {len(test_cases)}")
    print(f"  Exam kind: {metadata['exam_kind']} | required signatures: {len(metadata['required_signatures'])}")
    if metadata["extraction_status"] != "ok":
        print(f"  WARNING: LLM extraction failed ({metadata['extraction_error']})")

    print("Step 2: Checking constraint violations across all project files...")
    violations = check_constraints_project(project_dir, banned_names, language=language)
    print(f"  Found {len(violations)} violation(s)")

    static_results = None
    if language == "java":
        print("Step 2b: Deterministic requirement checks (signatures, ids, enums, scheduling, aspect, layering)...")
        static_results = run_static_checks(project_dir, instructions, metadata["required_signatures"])
        print(f"  {static_results['summary']}")

    test_results = []
    if test_cases:
        print("Step 3: Running test cases in sandbox...")
        test_results = run_test_cases_project(project_dir, entry_point, test_cases, language=language)
        summary = summarize_results(test_results)
        print(f"  {summary['passed']}/{summary['total']} passed")
    elif metadata["exam_kind"] == "service_api":
        print("Step 3: Service/API exam with no stdin/stdout examples: nothing to execute yet (needs a Spring test harness).")
    else:
        print("Step 3: No test cases found in instructions, skipping execution.")

    combined_source = _build_review_context(project_dir, language)

    print("Step 4: Generating holistic evaluation...")
    evaluation = evaluate_submission(instructions, combined_source, violations, test_results, static_results)

    return {
        "entry_point": entry_point,
        "language": language,
        "exam_kind": metadata["exam_kind"],
        "banned_names": banned_names,
        "extracted_test_cases": test_cases,
        "required_signatures": metadata["required_signatures"],
        "constraint_violations": violations,
        "requirement_checks": static_results["checks"] if static_results else [],
        "test_results": test_results,
        **build_evaluation_evidence(static_results, test_results, metadata["extraction_status"]),
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