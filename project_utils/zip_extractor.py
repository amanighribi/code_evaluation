import zipfile
import os
import uuid

MAX_UNCOMPRESSED_SIZE = 20 * 1024 * 1024  # 20 MB, generous for a student project
MAX_FILE_COUNT = 500

EXCLUDED_DIR_NAMES = {"venv", "__pycache__", ".git", "node_modules", ".idea", ".vscode"}


class UnsafeZipError(Exception):
    pass


def _is_safe_path(base_dir: str, target_path: str) -> bool:
    """Prevents zip-slip: ensures the resolved path stays inside base_dir."""
    resolved_base = os.path.realpath(base_dir)
    resolved_target = os.path.realpath(target_path)
    return resolved_target == resolved_base or resolved_target.startswith(resolved_base + os.sep)


def extract_zip_safely(zip_bytes: bytes, extract_root: str = None) -> str:
    """Safely extracts a zip archive's contents into a fresh temp directory.
    Validates against path traversal and zip-bomb style attacks.
    Returns the path to the extraction directory. Raises UnsafeZipError on any violation."""

    if extract_root is None:
        extract_root = os.path.join(os.path.dirname(__file__), "..", "project_tmp")

    run_id = uuid.uuid4().hex[:8]
    target_dir = os.path.join(extract_root, run_id)
    os.makedirs(target_dir, exist_ok=True)

    zip_path = os.path.join(target_dir, "_upload.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            infos = zf.infolist()

            if len(infos) > MAX_FILE_COUNT:
                raise UnsafeZipError(f"Zip contains too many files ({len(infos)} > {MAX_FILE_COUNT}).")

            total_size = sum(info.file_size for info in infos)
            if total_size > MAX_UNCOMPRESSED_SIZE:
                raise UnsafeZipError(
                    f"Zip uncompressed size too large ({total_size} bytes > {MAX_UNCOMPRESSED_SIZE} bytes)."
                )

            for info in infos:
                destination = os.path.join(target_dir, info.filename)
                if not _is_safe_path(target_dir, destination):
                    raise UnsafeZipError(f"Unsafe path detected in zip entry: {info.filename}")

            zf.extractall(target_dir)

    finally:
        os.remove(zip_path)  # don't leave the raw zip sitting in the extracted project

    return target_dir


def find_code_files(project_dir: str, extension: str) -> list:
    """Returns a list of file paths (relative to project_dir) matching the given
    extension, excluding common non-source directories."""
    matches = []
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES and not d.startswith(".")]
        for fname in files:
            if fname.endswith(extension):
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, project_dir)
                matches.append(rel_path)
    return matches


def cleanup_project_dir(project_dir: str):
    """Best-effort recursive cleanup of an extracted project directory."""
    for root, dirs, files in os.walk(project_dir, topdown=False):
        for fname in files:
            try:
                os.remove(os.path.join(root, fname))
            except OSError:
                pass
        for dname in dirs:
            try:
                os.rmdir(os.path.join(root, dname))
            except OSError:
                pass
    try:
        os.rmdir(project_dir)
    except OSError:
        pass


if __name__ == "__main__":
    import io

    # Build a small in-memory zip to test with
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("main.py", "print('hello')\n")
        zf.writestr("utils/helper.py", "def add(a, b):\n    return a + b\n")

    project_dir = extract_zip_safely(buf.getvalue())
    print("Extracted to:", project_dir)
    print("Python files found:", find_code_files(project_dir, ".py"))

    cleanup_project_dir(project_dir)
    print("Cleaned up:", not os.path.exists(project_dir))