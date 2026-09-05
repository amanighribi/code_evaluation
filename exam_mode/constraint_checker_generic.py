import re


def check_constraints_generic(source_code: str, banned_names: list) -> list:
    """Language-agnostic fallback constraint checker: scans for banned identifiers
    as whole-word matches anywhere in the code. Less precise than an AST-based
    checker (can false-positive on names appearing inside strings or comments),
    but works on any language without a dedicated parser."""

    violations = []
    lines = source_code.splitlines()

    for banned_name in banned_names:
        # Escape the name for regex safety, match whole identifier boundaries
        pattern = re.compile(r"\b" + re.escape(banned_name) + r"\b")

        for line_num, line in enumerate(lines, start=1):
            if pattern.search(line):
                violations.append({
                    "type": "banned_call",
                    "name": banned_name,
                    "line": line_num,
                    "message": (
                        f"Use of banned identifier '{banned_name}' at line {line_num} "
                        f"(detected via text scan; verify this is not inside a string or comment)."
                    ),
                })

    return violations


if __name__ == "__main__":
    test_code = """
#include <stdio.h>

int main() {
    int arr[5] = {5, 2, 4, 1, 3};
    qsort(arr, 5, sizeof(int), compare);
    return 0;
}
"""
    violations = check_constraints_generic(test_code, banned_names=["qsort", "sort"])
    for v in violations:
        print(v)