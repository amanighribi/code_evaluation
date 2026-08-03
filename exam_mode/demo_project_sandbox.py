import io
import zipfile
from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir
from exam_mode.sandbox_executor import run_python_project_in_sandbox

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as zf:
    zf.writestr("main.py", "from helper import add\n\nn1, n2 = map(int, input().split())\nprint(add(n1, n2))\n")
    zf.writestr("helper.py", "def add(a, b):\n    return a + b\n")

project_dir = extract_zip_safely(buf.getvalue())
try:
    result = run_python_project_in_sandbox(project_dir, "main.py", stdin_input="3 4\n", timeout=15)
    print(result)
finally:
    cleanup_project_dir(project_dir)