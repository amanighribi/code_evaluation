from exam_mode.test_runner import normalize_output


def test_collapses_multiple_spaces():
    assert normalize_output("1  2   3") == normalize_output("1 2 3")


def test_collapses_newlines_and_spaces():
    assert normalize_output("1\n2\n3") == normalize_output("1 2 3")


def test_strips_leading_trailing_whitespace():
    assert normalize_output("  1 2 3  \n") == "1 2 3"


def test_does_not_change_actual_content():
    assert normalize_output("1 2 3") != normalize_output("1 2 4")


def test_case_sensitivity_preserved():
    assert normalize_output("Hello") != normalize_output("hello")