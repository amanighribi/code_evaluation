from project_utils.zip_extractor import find_code_files

EXTENSION_BY_LANGUAGE = {"python": ".py", "java": ".java"}


class EntryPointError(Exception):
    pass


def resolve_entry_point(project_dir: str, language: str, requested_entry_point: str = None) -> str:
    """Determines which file to execute in a multi-file project.
    Returns the entry point path (relative to project_dir).
    Raises EntryPointError with a clear, actionable message if it cannot be resolved."""

    extension = EXTENSION_BY_LANGUAGE.get(language)
    if not extension:
        raise EntryPointError(f"Unsupported language: {language}")

    code_files = find_code_files(project_dir, extension)

    if not code_files:
        raise EntryPointError(f"No {extension} files found in the uploaded project.")

    if requested_entry_point:
        normalized_request = requested_entry_point.replace("\\", "/")
        normalized_files = [f.replace("\\", "/") for f in code_files]
        if normalized_request in normalized_files:
            return requested_entry_point
        raise EntryPointError(
            f"Specified entry_point '{requested_entry_point}' was not found in the project. "
            f"Available {extension} files: {normalized_files}"
        )

    if len(code_files) == 1:
        return code_files[0]

    raise EntryPointError(
        f"Project contains multiple {extension} files, and no entry_point was specified. "
        f"Please specify which file to run via the entry_point parameter. "
        f"Available files: {[f.replace(chr(92), '/') for f in code_files]}"
    )


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
        # Case 1: multiple files, no entry_point specified -> should raise
        try:
            resolve_entry_point(project_dir, "python")
        except EntryPointError as e:
            print("Expected error (no entry_point):", e)

        # Case 2: multiple files, correct entry_point specified -> should succeed
        result = resolve_entry_point(project_dir, "python", requested_entry_point="main.py")
        print("Resolved:", result)

        # Case 3: wrong entry_point specified -> should raise with helpful file list
        try:
            resolve_entry_point(project_dir, "python", requested_entry_point="nonexistent.py")
        except EntryPointError as e:
            print("Expected error (wrong entry_point):", e)
    finally:
        cleanup_project_dir(project_dir)