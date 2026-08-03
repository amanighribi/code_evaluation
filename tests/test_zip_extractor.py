import io
import zipfile
import os
import pytest
from project_utils.zip_extractor import (
    extract_zip_safely,
    find_code_files,
    cleanup_project_dir,
    UnsafeZipError,
)


def make_zip(entries: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return buf.getvalue()


def test_extracts_normal_zip_correctly():
    zip_bytes = make_zip({"main.py": "print('hi')\n", "utils/helper.py": "def f(): pass\n"})
    project_dir = extract_zip_safely(zip_bytes)
    try:
        files = find_code_files(project_dir, ".py")
        assert len(files) == 2
        assert any("main.py" in f for f in files)
        assert any("helper.py" in f for f in files)
    finally:
        cleanup_project_dir(project_dir)


def test_rejects_path_traversal_attempt():
    zip_bytes = make_zip({"../../evil.py": "print('escaped')\n"})
    with pytest.raises(UnsafeZipError):
        extract_zip_safely(zip_bytes)


def test_rejects_too_many_files():
    entries = {f"file_{i}.py": "pass\n" for i in range(600)}
    zip_bytes = make_zip(entries)
    with pytest.raises(UnsafeZipError):
        extract_zip_safely(zip_bytes)


def test_excludes_venv_and_pycache_dirs():
    zip_bytes = make_zip({
        "main.py": "print('hi')\n",
        "venv/lib/some_dependency.py": "pass\n",
        "__pycache__/main.cpython-311.pyc": "binary junk",
    })
    project_dir = extract_zip_safely(zip_bytes)
    try:
        files = find_code_files(project_dir, ".py")
        assert len(files) == 1
        assert "main.py" in files[0]
    finally:
        cleanup_project_dir(project_dir)


def test_cleanup_removes_directory_completely():
    zip_bytes = make_zip({"main.py": "print('hi')\n"})
    project_dir = extract_zip_safely(zip_bytes)
    cleanup_project_dir(project_dir)
    assert not os.path.exists(project_dir)