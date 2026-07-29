from exam_mode.constraint_checker_java import check_constraints_java


def test_detects_banned_bare_method_call():
    code = """
public class Sorter {
    public static void main(String[] args) {
        int[] arr = {1, 2, 3};
        sort(arr);
    }
    static void sort(int[] a) {}
}
"""
    violations = check_constraints_java(code, banned_names=["sort"])
    assert any(v["name"] == "sort" for v in violations)


def test_detects_banned_qualified_method_call():
    code = """
import java.util.Arrays;

public class Sorter {
    public static void main(String[] args) {
        int[] arr = {1, 2, 3};
        Arrays.sort(arr);
    }
}
"""
    violations = check_constraints_java(code, banned_names=["Arrays.sort"])
    assert any(v["name"] == "Arrays.sort" for v in violations)


def test_detects_banned_import():
    code = """
import java.util.Collections;

public class Foo {
    public static void main(String[] args) {}
}
"""
    violations = check_constraints_java(code, banned_names=["Collections"])
    assert any(v["type"] == "banned_import" for v in violations)


def test_no_violations_for_clean_code():
    code = """
public class BubbleSort {
    public static void main(String[] args) {
        int[] arr = {3, 1, 2};
        for (int i = 0; i < arr.length; i++) {
            for (int j = 0; j < arr.length - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
}
"""
    violations = check_constraints_java(code, banned_names=["sort"])
    assert violations == []


def test_handles_syntax_error_gracefully():
    broken_code = "public class Broken { void foo( }"
    violations = check_constraints_java(broken_code, banned_names=["sort"])
    assert len(violations) == 1
    assert violations[0]["type"] == "parse_error"