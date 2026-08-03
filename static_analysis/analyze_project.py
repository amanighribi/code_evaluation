import os
from static_analysis.analyzer import analyze_code
from project_utils.zip_extractor import find_code_files


def analyze_project(project_dir: str) -> dict:
    """Runs analyze_code() on every .py file in the project directory and
    aggregates the results into a single report."""

    py_files = find_code_files(project_dir, ".py")

    per_file_results = {}
    all_issues = []
    total_lines = 0
    total_functions = 0
    total_classes = 0
    files_with_errors = []

    for rel_path in py_files:
        full_path = os.path.join(project_dir, rel_path)
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            source_code = f.read()

        try:
            result = analyze_code(source_code)
        except SyntaxError as e:
            files_with_errors.append({"file": rel_path, "error": str(e)})
            continue

        for issue in result["issues"]:
            issue_with_file = dict(issue)
            issue_with_file["file"] = rel_path
            all_issues.append(issue_with_file)

        per_file_results[rel_path] = result
        total_lines += result["lines_of_code"]
        total_functions += result["num_functions"]
        total_classes += result["num_classes"]

    return {
        "files_analyzed": len(per_file_results),
        "files_with_syntax_errors": files_with_errors,
        "total_lines_of_code": total_lines,
        "total_functions": total_functions,
        "total_classes": total_classes,
        "total_issues": len(all_issues),
        "issues": all_issues,
        "per_file": per_file_results,
    }


if __name__ == "__main__":
    import io
    import zipfile
    from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("main.py", "import os\n\ndef foo():\n    return 1\n")
        zf.writestr("utils/helper.py", "def bar(a,b,c,d,e):\n    return a\n")

    project_dir = extract_zip_safely(buf.getvalue())
    try:
        report = analyze_project(project_dir)
        import json
        print(json.dumps(report, indent=2))
    finally:
        cleanup_project_dir(project_dir)