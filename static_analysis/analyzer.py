import ast
import hashlib


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
        self._check_unused_imports()
        self._check_bare_except()
        self._check_magic_numbers()
        self._check_unused_variables()
        self._check_duplicate_functions()
        return {
            "lines_of_code": len(self.source_code.splitlines()),
            "num_functions": len(self.functions),
            "num_classes": len(self.classes),
            "functions": self.functions,
            "classes": self.classes,
            "issues": self.issues,
        }

    # ---------- functions ----------

    def _visit_functions(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self._record_function(node)
                self._check_function_rules(node)

    def _record_function(self, node):
        complexity = self._cyclomatic_complexity(node)
        length = (node.end_lineno - node.lineno + 1) if hasattr(node, "end_lineno") else None
        has_docstring = ast.get_docstring(node) is not None
        num_params = len(node.args.args)

        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "num_params": num_params,
            "length": length,
            "cyclomatic_complexity": complexity,
            "has_docstring": has_docstring,
        })

    def _check_function_rules(self, node):
        has_docstring = ast.get_docstring(node) is not None
        num_params = len(node.args.args)
        complexity = self._cyclomatic_complexity(node)
        length = (node.end_lineno - node.lineno + 1) if hasattr(node, "end_lineno") else None

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

    def _cyclomatic_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    # ---------- classes ----------

    def _visit_classes(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self.classes.append({"name": node.name, "line": node.lineno})
                if not node.name[0].isupper():
                    self.issues.append(f"Class '{node.name}' (line {node.lineno}) does not follow PascalCase naming.")

    # ---------- unused imports ----------

    def _check_unused_imports(self):
        imported_names = self._collect_imported_names()
        used_names = self._collect_used_names()

        for name, line in imported_names.items():
            if name not in used_names:
                self.issues.append(f"Import '{name}' (line {line}) is unused.")

    def _collect_imported_names(self):
        imported_names = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    imported_names[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_names[name] = node.lineno
        return imported_names

    def _collect_used_names(self):
        return {node.id for node in ast.walk(self.tree) if isinstance(node, ast.Name)}

    # ---------- bare except ----------

    def _check_bare_except(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                self.issues.append(f"Bare 'except:' clause (line {node.lineno}) hides errors; specify an exception type.")

    # ---------- magic numbers ----------

    def _check_magic_numbers(self, allowed=(0, 1, -1)):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Compare):
                self._flag_magic_numbers_in_compare(node, allowed)

    def _flag_magic_numbers_in_compare(self, node, allowed):
        for comparator in node.comparators + [node.left]:
            if self._is_magic_number(comparator, allowed):
                self.issues.append(
                    f"Magic number {comparator.value} used in comparison (line {node.lineno}); consider a named constant."
                )

    def _is_magic_number(self, comparator, allowed):
        return (
            isinstance(comparator, ast.Constant)
            and isinstance(comparator.value, (int, float))
            and comparator.value not in allowed
        )

    # ---------- unused variables ----------

    def _check_unused_variables(self):
        for func_node in ast.walk(self.tree):
            if isinstance(func_node, ast.FunctionDef):
                self._check_unused_variables_in_function(func_node)

    def _check_unused_variables_in_function(self, func_node):
        assigned, used = self._collect_assigned_and_used(func_node)
        for name, line in assigned.items():
            if name not in used and not name.startswith("_"):
                self.issues.append(f"Variable '{name}' (line {line}) in function '{func_node.name}' is assigned but never used.")

    def _collect_assigned_and_used(self, func_node):
        assigned = {}
        used = set()
        for node in ast.walk(func_node):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned[node.id] = node.lineno
                elif isinstance(node.ctx, ast.Load):
                    used.add(node.id)
        return assigned, used

    # ---------- duplicate functions ----------

    def _check_duplicate_functions(self):
        seen = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self._check_duplicate(node, seen)

    def _check_duplicate(self, node, seen):
        fingerprint = self._fingerprint(node)
        if fingerprint in seen:
            self.issues.append(
                f"Function '{node.name}' (line {node.lineno}) appears to duplicate '{seen[fingerprint]}'."
            )
        else:
            seen[fingerprint] = node.name

    def _fingerprint(self, node):
        body_dump = ast.dump(node, annotate_fields=False)
        normalized = body_dump.replace(node.name, "FUNC", 1)
        return hashlib.md5(normalized.encode()).hexdigest()


def analyze_code(source_code: str) -> dict:
    analyzer = CodeAnalyzer(source_code)
    return analyzer.analyze()