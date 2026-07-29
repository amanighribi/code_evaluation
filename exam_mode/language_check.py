import re


def looks_like_python(code: str) -> bool:
    # Signals that are NOT valid/common in Java, to avoid overlap (e.g. "import" exists in both languages)
    python_only_signals = [
        r"\bdef\s+\w+\s*\(",       # def foo(
        r"\bprint\s*\(",            # print(...)
        r"^\s*#",                   # Python comments
        r"\belif\b",
        r":\s*$",                   # trailing colon (if/for/def/class headers), checked per-line below
    ]
    return any(re.search(pattern, code, re.MULTILINE) for pattern in python_only_signals)


def looks_like_java(code: str) -> bool:
    java_only_signals = [
        r"\bpublic\s+class\s+\w+",
        r"\bclass\s+\w+\s*{",
        r"\bpublic\s+static\s+void\s+main\s*\(",
        r"\bSystem\.out\.print",
        r";\s*$",                   # statements ending in semicolons, checked per-line below
    ]
    return any(re.search(pattern, code, re.MULTILINE) for pattern in java_only_signals)


def check_language_matches(code: str, declared_language: str) -> str | None:
    """Returns a warning message if the code doesn't look like the declared language, else None.
    This is a heuristic sanity check, not a guarantee - it only catches obvious mismatches."""

    is_python = looks_like_python(code)
    is_java = looks_like_java(code)

    if declared_language == "python":
        if is_java and not is_python:
            return (
                "The uploaded code looks like Java, but language='python' was specified. "
                "Please check the language parameter matches the uploaded file."
            )
    elif declared_language == "java":
        if is_python and not is_java:
            return (
                "The uploaded code looks like Python, but language='java' was specified. "
                "Please check the language parameter matches the uploaded file."
            )

    return None


if __name__ == "__main__":
    java_code = """
import java.util.Scanner;

public class Foo {
    public static void main(String[] args) {
        System.out.println("hi");
    }
}
"""
    python_code = "def foo():\n    print('hi')\n"

    print("Java code declared as python:", check_language_matches(java_code, "python"))
    print("Python code declared as java:", check_language_matches(python_code, "java"))
    print("Python code declared as python:", check_language_matches(python_code, "python"))
    print("Java code declared as java:", check_language_matches(java_code, "java"))