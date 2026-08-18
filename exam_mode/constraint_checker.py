import ast
import os
from exam_mode.constraint_checker_java import check_constraints_java


class ConstraintChecker(ast.NodeVisitor):
    """Checks student code against a list of banned functions, methods, or imports,
    as specified by exam instructions (e.g. 'do not use sort() or sorted()')."""

    def __init__(self, source_code: str, banned_names: list[str]):
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self.banned_names = set(banned_names)
        self.violations = []

    def check(self) -> list[dict]:
        self._check_calls()
        self._check_imports()
        return self.violations

    def _check_calls(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                called_name = self._get_call_name(node)
                if called_name and called_name in self.banned_names:
                    self.violations.append({
                        "type": "banned_call",
                        "name": called_name,
                        "line": node.lineno,
                        "message": f"Use of banned function/method '{called_name}' at line {node.lineno}.",
                    })

    def _get_call_name(self, call_node: ast.Call):
        func = call_node.func
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _check_imports(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name.split(".")[0]
                    if name in self.banned_names:
                        self.violations.append({
                            "type": "banned_import",
                            "name": name,
                            "line": node.lineno,
                            "message": f"Import of banned module '{name}' at line {node.lineno}.",
                        })
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in self.banned_names:
                    self.violations.append({
                        "type": "banned_import",
                        "name": node.module,
                        "line": node.lineno,
                        "message": f"Import from banned module '{node.module}' at line {node.lineno}.",
                    })


def check_constraints(source_code: str, banned_names: list[str]) -> list[dict]:
    checker = ConstraintChecker(source_code, banned_names)
    return checker.check()


def check_constraints_multilang(source_code: str, banned_names: list[str], language: str) -> list[dict]:
    """Dispatches to the correct language-specific constraint checker.
    language should be 'python' or 'java'."""
    if language == "python":
        return check_constraints(source_code, banned_names)
    elif language == "java":
        return check_constraints_java(source_code, banned_names)
    else:
        raise ValueError(f"Unsupported language: {language}. Supported: 'python', 'java'.")


if __name__ == "__main__":
    test_code = """
import itertools

def bubble_sort(arr):
    return sorted(arr)

def another_approach(data):
    data.sort()
    return data
"""
    violations = check_constraints(test_code, banned_names=["sort", "sorted", "itertools"])
    for v in violations:
        print(v)
from project_utils.zip_extractor import find_code_files


def check_constraints_project(project_dir: str, banned_names: list, language: str) -> list:
    """Scans every source file in the project (not just the entry point) for constraint
    violations, since a student could hide a banned call/import in any file."""

    extension = ".py" if language == "python" else ".java"
    code_files = find_code_files(project_dir, extension)

    all_violations = []
    for rel_path in code_files:
        full_path = os.path.join(project_dir, rel_path)
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            source_code = f.read()

        try:
            violations = check_constraints_multilang(source_code, banned_names, language=language)
        except SyntaxError:
            continue  # a broken file will already surface as a compile/parse error elsewhere

        for v in violations:
            v_with_file = dict(v)
            v_with_file["file"] = rel_path
            all_violations.append(v_with_file)

    return all_violations