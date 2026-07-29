from exam_mode.constraint_checker import check_constraints, check_constraints_multilang


def test_detects_banned_function_call():
    code = "def foo(arr):\n    return sorted(arr)\n"
    violations = check_constraints(code, banned_names=["sorted"])
    assert len(violations) == 1
    assert violations[0]["type"] == "banned_call"
    assert violations[0]["name"] == "sorted"


def test_detects_banned_method_call():
    code = "def foo(arr):\n    arr.sort()\n    return arr\n"
    violations = check_constraints(code, banned_names=["sort"])
    assert len(violations) == 1
    assert violations[0]["name"] == "sort"


def test_detects_banned_import():
    code = "import itertools\n\ndef foo():\n    pass\n"
    violations = check_constraints(code, banned_names=["itertools"])
    assert len(violations) == 1
    assert violations[0]["type"] == "banned_import"


def test_detects_banned_import_from():
    code = "from itertools import permutations\n\ndef foo():\n    pass\n"
    violations = check_constraints(code, banned_names=["itertools"])
    assert len(violations) == 1


def test_no_violations_for_clean_code():
    code = "def bubble_sort(arr):\n    n = len(arr)\n    return arr\n"
    violations = check_constraints(code, banned_names=["sort", "sorted"])
    assert violations == []


def test_multiple_violations_detected():
    code = "import itertools\n\ndef foo(arr):\n    return sorted(arr)\n"
    violations = check_constraints(code, banned_names=["sorted", "itertools"])
    assert len(violations) == 2


def test_multilang_dispatches_to_python():
    code = "def foo(arr):\n    return sorted(arr)\n"
    violations = check_constraints_multilang(code, ["sorted"], language="python")
    assert len(violations) == 1


def test_multilang_rejects_unsupported_language():
    import pytest
    with pytest.raises(ValueError):
        check_constraints_multilang("code", ["x"], language="cobol")