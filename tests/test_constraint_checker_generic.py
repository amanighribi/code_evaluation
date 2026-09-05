from exam_mode.constraint_checker_generic import check_constraints_generic
from exam_mode.constraint_checker import check_constraints_multilang, is_precise_language


def test_detects_banned_identifier():
    code = "int main() {\n    qsort(arr, 5, sizeof(int), cmp);\n    return 0;\n}\n"
    violations = check_constraints_generic(code, banned_names=["qsort"])
    assert len(violations) == 1
    assert violations[0]["name"] == "qsort"


def test_no_false_positive_on_partial_word_match():
    code = "int quicksort_helper(int x) { return x; }\n"
    violations = check_constraints_generic(code, banned_names=["sort"])
    assert violations == []  # "sort" should not match inside "quicksort_helper"


def test_no_violations_in_clean_code():
    code = "int add(int a, int b) { return a + b; }\n"
    violations = check_constraints_generic(code, banned_names=["qsort", "system"])
    assert violations == []


def test_multiple_occurrences_all_detected():
    code = "sort(a);\nsort(b);\n"
    violations = check_constraints_generic(code, banned_names=["sort"])
    assert len(violations) == 2


def test_dispatcher_routes_unknown_language_to_generic():
    code = "qsort(arr);\n"
    violations = check_constraints_multilang(code, banned_names=["qsort"], language="c")
    assert len(violations) == 1


def test_is_precise_language():
    assert is_precise_language("python") is True
    assert is_precise_language("java") is True
    assert is_precise_language("c") is False
    assert is_precise_language("javascript") is False