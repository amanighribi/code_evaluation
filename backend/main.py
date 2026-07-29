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

app = FastAPI(title="Subject 9 - Code Evaluation API")


@app.get("/")
def root():
    return {"message": "Code Evaluation API is running"}


@app.post("/analyze")
def analyze(file: UploadFile = File(...)):
    content = file.file.read()

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
):
    code_content = code_file.file.read()
    instructions_content = instructions_file.file.read()

    try:
        student_code = code_content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Code file is not valid UTF-8 text.")

    try:
        instructions = instructions_content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Instructions file is not valid UTF-8 text.")

    if language not in ("python", "java"):
        raise HTTPException(status_code=400, detail="language must be 'python' or 'java'.")
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