import io
import zipfile
from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir
from exam_mode.constraint_checker import check_constraints_project

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as zf:
    zf.writestr("main.py", "from helper import do_sort\n\narr = [3, 1, 2]\nprint(do_sort(arr))\n")
    zf.writestr("helper.py", "def do_sort(arr):\n    return sorted(arr)\n")

project_dir = extract_zip_safely(buf.getvalue())
try:
    violations = check_constraints_project(project_dir, banned_names=["sorted"], language="python")
    for v in violations:
        print(v)
finally:
    cleanup_project_dir(project_dir)