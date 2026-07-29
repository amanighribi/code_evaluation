from exam_mode.language_check import check_language_matches


def test_detects_java_declared_as_python():
    java_code = "public class Foo { public static void main(String[] args) {} }"
    warning = check_language_matches(java_code, "python")
    assert warning is not None


def test_detects_python_declared_as_java():
    python_code = "def foo():\n    print('hi')\n"
    warning = check_language_matches(python_code, "java")
    assert warning is not None


def test_no_warning_for_matching_python():
    python_code = "def foo():\n    print('hi')\n"
    assert check_language_matches(python_code, "python") is None


def test_no_warning_for_matching_java():
    java_code = "public class Foo { public static void main(String[] args) {} }"
    assert check_language_matches(java_code, "java") is None


def test_java_with_import_not_confused_for_python():
    java_code = """
import java.util.Scanner;

public class Foo {
    public static void main(String[] args) {
        System.out.println("hi");
    }
}
"""
    warning = check_language_matches(java_code, "python")
    assert warning is not None