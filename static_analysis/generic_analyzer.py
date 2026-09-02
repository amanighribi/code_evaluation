import re

MAX_LINE_LENGTH = 120
MAX_NESTING_DEPTH = 4
MAX_FILE_LINES = 400
TODO_PATTERN = re.compile(r"\b(TODO|FIXME)\b", re.IGNORECASE)


def analyze_generic(source_code: str) -> dict:
    """Language-agnostic static analysis for any text-based source file.
    Less precise than an AST-based analyzer, but works on any language
    without needing a dedicated parser."""

    lines = source_code.splitlines()
    issues = []

    issues.extend(_check_line_length(lines))
    issues.extend(_check_trailing_whitespace(lines))
    issues.extend(_check_todo_comments(lines))
    issues.extend(_check_nesting_depth(lines))
    issues.extend(_check_file_length(lines))

    return {
        "lines_of_code": len(lines),
        "num_functions": None,   # not determinable without a language-specific parser
        "num_classes": None,
        "functions": [],
        "classes": [],
        "issues": issues,
    }


def _check_line_length(lines):
    issues = []
    for i, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            issues.append({
                "rule_id": "line_too_long",
                "message": f"Line {i} is {len(line)} characters long (over {MAX_LINE_LENGTH}).",
            })
    return issues


def _check_trailing_whitespace(lines):
    issues = []
    for i, line in enumerate(lines, start=1):
        if line != line.rstrip() and line.strip():
            issues.append({
                "rule_id": "trailing_whitespace",
                "message": f"Line {i} has trailing whitespace.",
            })
    return issues


def _check_todo_comments(lines):
    issues = []
    for i, line in enumerate(lines, start=1):
        if TODO_PATTERN.search(line):
            issues.append({
                "rule_id": "todo_comment_left",
                "message": f"Unresolved TODO/FIXME marker at line {i}.",
            })
    return issues


def _estimate_indent_level(line, indent_unit=4):
    """Rough heuristic: counts leading whitespace, normalized to a 4-space unit.
    Not exact for tab-indented or brace-based languages, but a reasonable proxy."""
    stripped = line.lstrip(" \t")
    leading = line[: len(line) - len(stripped)]
    spaces = leading.replace("\t", " " * indent_unit)
    return len(spaces) // indent_unit


def _check_nesting_depth(lines):
    issues = []
    max_seen = 0
    max_line = None
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        depth = _estimate_indent_level(line)
        if depth > max_seen:
            max_seen = depth
            max_line = i
    if max_seen > MAX_NESTING_DEPTH:
        issues.append({
            "rule_id": "deep_nesting",
            "message": f"Nesting reaches an estimated depth of {max_seen} around line {max_line} (over {MAX_NESTING_DEPTH}).",
        })
    return issues


def _check_file_length(lines):
    issues = []
    if len(lines) > MAX_FILE_LINES:
        issues.append({
            "rule_id": "file_too_long",
            "message": f"File is {len(lines)} lines long (over {MAX_FILE_LINES}).",
        })
    return issues


if __name__ == "__main__":
    import json
    test_code = """function foo() {
    if (true) {
        for (let i = 0; i < 10; i++) {
            if (i > 5) {
                if (i > 8) {
                    console.log("deep");   
                }
            }
        }
    }
}
// TODO: clean this up later
"""
    result = analyze_generic(test_code)
    print(json.dumps(result, indent=2))