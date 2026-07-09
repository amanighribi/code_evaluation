from fastapi import FastAPI, UploadFile, File
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from static_analysis.analyzer import analyze_code

app = FastAPI(title="Subject 9 - Code Evaluation API")


@app.get("/")
def root():
    return {"message": "Code Evaluation API is running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    source_code = content.decode("utf-8")
    result = analyze_code(source_code)
    return result