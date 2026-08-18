import io
import zipfile
from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir
from exam_mode.constraint_checker import check_constraints_project


def make_project(entries: dict) -> str:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return extract_zip_safely(buf.getvalue())


def test_finds_violation_hidden_in_non_entry_file():
    project_dir = make_project({
        "main.py": "from helper import do_sort\nprint(do_sort([3, 1, 2]))\n",
        "helper.py": "def do_sort(arr):\n    return sorted(arr)\n",
    })
    try:
        violations = check_constraints_project(project_dir, banned_names=["sorted"], language="python")
        assert len(violations) == 1
        assert violations[0]["file"] == "helper.py"
    finally:
        cleanup_project_dir(project_dir)


def test_no_violations_across_clean_project():
    project_dir = make_project({
        "main.py": "print('hello')\n",
        "helper.py": "def f(a, b):\n    return a + b\n",
    })
    try:
        violations = check_constraints_project(project_dir, banned_names=["sorted", "sort"], language="python")
        assert violations == []
    finally:
        cleanup_project_dir(project_dir)


def test_finds_violations_across_multiple_files():
    project_dir = make_project({
        "main.py": "arr = [1, 2, 3]\narr.sort()\n",
        "helper.py": "def f(arr):\n    return sorted(arr)\n",
    })
    try:
        violations = check_constraints_project(project_dir, banned_names=["sort", "sorted"], language="python")
        assert len(violations) == 2
        files_flagged = {v["file"] for v in violations}
        assert files_flagged == {"main.py", "helper.py"}
    finally:
        cleanup_project_dir(project_dir)