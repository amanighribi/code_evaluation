from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import sys
import os
import json


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from static_analysis.analyzer import analyze_code
from rag.retrieve import get_rubric_for_rule
from llm.generate_feedback import generate_batch_feedback
from exam_mode.full_exam_pipeline import run_full_exam_evaluation
from exam_mode.language_check import check_language_matches
from exam_mode.full_exam_pipeline import run_full_exam_evaluation, run_full_exam_evaluation_project
from exam_mode.entry_point_resolver import EntryPointError
from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir, UnsafeZipError
from static_analysis.analyze_project import analyze_project

app = FastAPI(title="Subject 9 - Code Evaluation API")


@app.get("/")
def root():
    return {"message": "Code Evaluation API is running"}


@app.post("/analyze")
def analyze(file: UploadFile = File(...)):
    content = file.file.read()
    filename = file.filename or ""
    


    if filename.lower().endswith(".zip"):
        try:
            project_dir = extract_zip_safely(content)
        except UnsafeZipError as e:
            raise HTTPException(status_code=400, detail=f"Unsafe or invalid zip file: {e}")

        try:
            report = analyze_project(project_dir)

            for rel_path, file_result in report["per_file"].items():
                if not file_result["issues"]:
                    continue

                full_path = os.path.join(project_dir, rel_path)
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    file_source = f.read()

                issues_with_rubrics = []
                for issue in file_result["issues"]:
                    rubric = get_rubric_for_rule(issue["rule_id"])
                    issues_with_rubrics.append({
                        "rule_id": issue["rule_id"],
                        "issue": issue["message"],
                        "rubric": rubric,
                    })

                feedback_list = generate_batch_feedback(issues_with_rubrics, file_source)

                feedback_by_rule_id = {}
                for entry in feedback_list:
                    feedback_by_rule_id.setdefault(entry.get("rule_id"), []).append(entry.get("feedback"))

                for issue in file_result["issues"]:
                    matches = feedback_by_rule_id.get(issue["rule_id"], [])
                    issue["feedback"] = matches.pop(0) if matches else None

            # keep the flat "issues" list in sync with the per-file feedback we just added
            for issue in report["issues"]:
                file_issues = report["per_file"][issue["file"]]["issues"]
                match = next((fi for fi in file_issues if fi["rule_id"] == issue["rule_id"] and fi["message"] == issue["message"]), None)
                if match:
                    issue["feedback"] = match.get("feedback")

            return report

        finally:
            cleanup_project_dir(project_dir)

    else:
        try:
            source_code = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File is not valid UTF-8 text.")

        try:
            result = analyze_code(source_code)
        except SyntaxError as e:
            raise HTTPException(status_code=400, detail=f"Invalid Python syntax: {e}")

        issues_with_rubrics = []
        for issue in result["issues"]:
            rule_id = issue["rule_id"]
            rubric = get_rubric_for_rule(rule_id)
            issues_with_rubrics.append({
                "rule_id": rule_id,
                "issue": issue["message"],
                "rubric": rubric,
            })

        feedback_list = generate_batch_feedback(issues_with_rubrics, source_code)

        feedback_by_rule_id = {}
        for entry in feedback_list:
            feedback_by_rule_id.setdefault(entry.get("rule_id"), []).append(entry.get("feedback"))

        for issue in result["issues"]:
            rule_id = issue["rule_id"]
            matches = feedback_by_rule_id.get(rule_id, [])
            issue["feedback"] = matches.pop(0) if matches else None

        return result
@app.post("/evaluate-exam")
def evaluate_exam(
    code_file: UploadFile = File(...),
    instructions_file: UploadFile = File(...),
    language: str = Form(default="python"),
    entry_point: str = Form(default=None),
):
    code_content = code_file.file.read()
    instructions_content = instructions_file.file.read()
    code_filename = code_file.filename or ""

    try:
        instructions = instructions_content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Instructions file is not valid UTF-8 text.")

    if language not in ("python", "java"):
        raise HTTPException(status_code=400, detail="language must be 'python' or 'java'.")

    if code_filename.lower().endswith(".zip"):
        try:
            project_dir = extract_zip_safely(code_content)
        except UnsafeZipError as e:
            raise HTTPException(status_code=400, detail=f"Unsafe or invalid zip file: {e}")

        try:
            result = run_full_exam_evaluation_project(
                instructions=instructions,
                project_dir=project_dir,
                language=language,
                requested_entry_point=entry_point,
            )
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            return result
        finally:
            cleanup_project_dir(project_dir)

    else:
        try:
            student_code = code_content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Code file is not valid UTF-8 text.")

        language_warning = check_language_matches(student_code, language)
        if language_warning:
            raise HTTPException(status_code=400, detail=language_warning)

        try:
            result = run_full_exam_evaluation(
                instructions=instructions,
                student_code=student_code,
                language=language,
            )
        except SyntaxError as e:
            raise HTTPException(status_code=400, detail=f"Invalid {language} syntax: {e}")

        return result