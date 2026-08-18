import io
import zipfile
import json
from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir
from exam_mode.full_exam_pipeline import run_full_exam_evaluation_project

instructions = """
Write a program with two files: main.py should read two integers and print their sum,
computed by a function in helper.py. Do not use eval() anywhere.

For example, given the input 3 and 4, the output should be: 7
"""

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as zf:
    zf.writestr("main.py", "from helper import add\n\na = int(input())\nb = int(input())\nprint(add(a, b))\n")
    zf.writestr("helper.py", "def add(a, b):\n    return a + b\n")

project_dir = extract_zip_safely(buf.getvalue())
try:
    result = run_full_exam_evaluation_project(instructions, project_dir, language="python", requested_entry_point="main.py")
    print(json.dumps(result, indent=2, ensure_ascii=False))
finally:
    cleanup_project_dir(project_dir)