import os
import re

from project_utils.zip_extractor import find_code_files

EXTENSION_BY_LANGUAGE = {"python": ".py", "java": ".java"}

# Build output / IDE / VCS / virtualenv folders are never student source.
IGNORED_DIRS = {
    "target", "build", "out", ".idea", ".git", ".mvn", ".gradle",
    "node_modules", "__pycache__", "venv", ".venv", "env", "__MACOSX",
}
BUILD_FILES = {"pom.xml", "build.gradle", "build.gradle.kts"}


class EntryPointError(Exception):
    pass


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _is_ignored(rel_path: str) -> bool:
    parts = _norm(rel_path).split("/")[:-1]
    return any(p in IGNORED_DIRS for p in parts)


def _is_test_path(rel_path: str) -> bool:
    p = "/" + _norm(rel_path)
    name = p.rsplit("/", 1)[-1]
    return "/src/test/" in p or "/tests/" in p or name.startswith("test_") or name.endswith("Test.java") or name.endswith("Tests.java")


def _read(project_dir: str, rel_path: str) -> str:
    try:
        with open(os.path.join(project_dir, rel_path), "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def _has_build_file(project_dir: str) -> bool:
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        if BUILD_FILES.intersection(files):
            return True
    return False


def detect_language(project_dir: str) -> str:
    """language='auto': infer 'java' or 'python' from the project contents."""
    counts = {}
    for lang, ext in EXTENSION_BY_LANGUAGE.items():
        n = len([f for f in find_code_files(project_dir, ext) if not _is_ignored(f)])
        if n:
            counts[lang] = n
    if not counts:
        raise EntryPointError("No .py or .java source files found in the uploaded project.")
    if len(counts) == 1:
        return next(iter(counts))
    if _has_build_file(project_dir):
        return "java"
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    if ranked[0][1] == ranked[1][1]:
        raise EntryPointError(f"Cannot auto-detect language (found {counts}). Please specify language.")
    return ranked[0][0]


def _score(project_dir: str, rel_path: str, language: str) -> int:
    text = _read(project_dir, rel_path)
    name = _norm(rel_path).rsplit("/", 1)[-1]
    score = 0
    if language == "java":
        if "@SpringBootApplication" in text:
            score += 100
        if re.search(r"public\s+static\s+void\s+main\s*\(", text):
            score += 50
    else:
        if re.search(r"""if\s+__name__\s*==\s*['"]__main__['"]""", text):
            score += 100
        if name in {"main.py", "app.py", "__main__.py"}:
            score += 20
    if score and _is_test_path(rel_path):
        score -= 200
    return score


def _auto_pick(project_dir: str, candidates: list, language: str) -> str:
    scored = sorted(((_score(project_dir, f, language), f) for f in candidates), reverse=True)
    scored = [(s, f) for s, f in scored if s > 0]
    if not scored:
        raise EntryPointError(
            "Could not auto-detect an entry point (no @SpringBootApplication / main method / "
            "__main__ guard found). Please specify entry_point. "
            f"Available files: {[_norm(f) for f in candidates]}"
        )
    top = scored[0][0]
    tied = [f for s, f in scored if s == top]
    if len(tied) > 1:
        raise EntryPointError(
            f"Multiple equally likely entry points found: {[_norm(f) for f in tied]}. "
            "Please specify entry_point."
        )
    return tied[0]


def list_source_files(project_dir: str, language: str, include_tests: bool = False) -> list:
    """Student source files worth showing to a reviewer: no build output, IDE folders or (by default) tests."""
    extension = EXTENSION_BY_LANGUAGE.get(language)
    if not extension:
        return []
    files = [f for f in find_code_files(project_dir, extension) if not _is_ignored(f)]
    if not include_tests:
        files = [f for f in files if not _is_test_path(f)]
    return files


def resolve_project(project_dir: str, language: str = None, requested_entry_point: str = None):
    """Returns (language, entry_point). `language` may be None/''/'auto' to auto-detect."""
    if not language or language.lower() == "auto":
        language = detect_language(project_dir)
    language = language.lower()
    return language, resolve_entry_point(project_dir, language, requested_entry_point)


def resolve_entry_point(project_dir: str, language: str, requested_entry_point: str = None) -> str:
    """Determines which file to execute in a multi-file project.
    Returns the entry point path (relative to project_dir).
    Raises EntryPointError with a clear, actionable message if it cannot be resolved.
    `language` may be 'auto'. `requested_entry_point` may be empty/None/'auto' to auto-detect."""

    if not language or language.lower() == "auto":
        language = detect_language(project_dir)
    language = language.lower()

    extension = EXTENSION_BY_LANGUAGE.get(language)
    if not extension:
        raise EntryPointError(f"Unsupported language: {language}")

    code_files = find_code_files(project_dir, extension)
    if not code_files:
        raise EntryPointError(f"No {extension} files found in the uploaded project.")

    if requested_entry_point and requested_entry_point.strip().lower() != "auto":
        normalized_request = _norm(requested_entry_point).lstrip("./")
        by_norm = {_norm(f): f for f in code_files}
        if normalized_request in by_norm:
            return requested_entry_point
        # Tolerate a unique suffix match, e.g. "ExamenApplication.java" or "examen/ExamenApplication.java"
        suffix_hits = [f for n, f in by_norm.items() if n.endswith("/" + normalized_request)]
        if len(suffix_hits) == 1:
            return suffix_hits[0]
        if len(suffix_hits) > 1:
            raise EntryPointError(
                f"entry_point '{requested_entry_point}' is ambiguous. Matches: {[_norm(f) for f in suffix_hits]}"
            )
        raise EntryPointError(
            f"Specified entry_point '{requested_entry_point}' was not found in the project. "
            f"Available {extension} files: {list(by_norm)}"
        )

    # No entry point requested: ignore build output / IDE folders, then decide.
    candidates = [f for f in code_files if not _is_ignored(f)] or code_files
    if len(candidates) == 1:
        return candidates[0]
    return _auto_pick(project_dir, candidates, language)


if __name__ == "__main__":
    import io
    import zipfile
    from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("main.py", "print('hi')\n")
        zf.writestr("helper.py", "def f(): pass\n")

    project_dir = extract_zip_safely(buf.getvalue())
    try:
        # Multiple files, no __main__ guard anywhere -> should still raise (actionable error)
        try:
            resolve_entry_point(project_dir, "python")
        except EntryPointError as e:
            print("Expected error (no entry_point):", e)
        print("Resolved:", resolve_entry_point(project_dir, "python", requested_entry_point="main.py"))
        try:
            resolve_entry_point(project_dir, "python", requested_entry_point="nonexistent.py")
        except EntryPointError as e:
            print("Expected error (wrong entry_point):", e)
    finally:
        cleanup_project_dir(project_dir)