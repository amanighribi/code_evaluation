import ast


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self.functions = []
        self.classes = []
        self.issues = []

    def analyze(self):
        self._visit_functions()
        self._visit_classes()
        return {
            "lines_of_code": len(self.source_code.splitlines()),
            "num_functions": len(self.functions),
            "num_classes": len(self.classes),
            "functions": self.functions,
            "classes": self.classes,
            "issues": self.issues,
        }

    def _visit_functions(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._cyclomatic_complexity(node)
                length = (node.end_lineno - node.lineno + 1) if hasattr(node, "end_lineno") else None
                has_docstring = ast.get_docstring(node) is not None
                num_params = len(node.args.args)

                func_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "num_params": num_params,
                    "length": length,
                    "cyclomatic_complexity": complexity,
                    "has_docstring": has_docstring,
                }
                self.functions.append(func_info)

                # Rule-based issue detection
                if not has_docstring:
                    self.issues.append(f"Function '{node.name}' (line {node.lineno}) is missing a docstring.")
                if num_params > 4:
                    self.issues.append(f"Function '{node.name}' (line {node.lineno}) has too many parameters ({num_params}).")
                if complexity > 5:
                    self.issues.append(f"Function '{node.name}' (line {node.lineno}) has high cyclomatic complexity ({complexity}).")
                if length and length > 30:
                    self.issues.append(f"Function '{node.name}' (line {node.lineno}) is too long ({length} lines).")
                if not node.name.islower() or " " in node.name:
                    self.issues.append(f"Function '{node.name}' (line {node.lineno}) does not follow snake_case naming.")

    def _visit_classes(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self.classes.append({"name": node.name, "line": node.lineno})
                if not node.name[0].isupper():
                    self.issues.append(f"Class '{node.name}' (line {node.lineno}) does not follow PascalCase naming.")

    def _cyclomatic_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity


def analyze_code(source_code: str) -> dict:
    analyzer = CodeAnalyzer(source_code)
    return analyzer.analyze()