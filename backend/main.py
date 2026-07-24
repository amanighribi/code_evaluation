from fastapi import FastAPI, UploadFile, File, HTTPException
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from static_analysis.analyzer import analyze_code
from rag.retrieve import get_rubric_for_rule
from llm.generate_feedback import generate_batch_feedback

app = FastAPI(title="Code Evaluation API")


@app.get("/")
def root():
    return {"message": "Code Evaluation API is running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()

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