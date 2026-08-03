import io
import zipfile
import pytest
from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir
from exam_mode.entry_point_resolver import resolve_entry_point, EntryPointError


def make_project(entries: dict) -> str:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return extract_zip_safely(buf.getvalue())


def test_single_file_auto_resolves():
    project_dir = make_project({"main.py": "print('hi')\n"})
    try:
        assert resolve_entry_point(project_dir, "python") == "main.py"
    finally:
        cleanup_project_dir(project_dir)


def test_multiple_files_without_entry_point_raises():
    project_dir = make_project({"main.py": "print('hi')\n", "helper.py": "pass\n"})
    try:
        with pytest.raises(EntryPointError):
            resolve_entry_point(project_dir, "python")
    finally:
        cleanup_project_dir(project_dir)


def test_multiple_files_with_correct_entry_point_resolves():
    project_dir = make_project({"main.py": "print('hi')\n", "helper.py": "pass\n"})
    try:
        assert resolve_entry_point(project_dir, "python", "main.py") == "main.py"
    finally:
        cleanup_project_dir(project_dir)


def test_wrong_entry_point_raises_with_helpful_message():
    project_dir = make_project({"main.py": "print('hi')\n"})
    try:
        with pytest.raises(EntryPointError, match="not found"):
            resolve_entry_point(project_dir, "python", "wrong.py")
    finally:
        cleanup_project_dir(project_dir)


def test_no_code_files_raises():
    project_dir = make_project({"readme.txt": "hello\n"})
    try:
        with pytest.raises(EntryPointError, match="No .py files"):
            resolve_entry_point(project_dir, "python")
    finally:
        cleanup_project_dir(project_dir)