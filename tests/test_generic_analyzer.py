from static_analysis.generic_analyzer import analyze_generic


def test_detects_long_line():
    code = "x = 1 " + "+ 1 " * 40
    result = analyze_generic(code)
    assert any(i["rule_id"] == "line_too_long" for i in result["issues"])


def test_detects_trailing_whitespace():
    code = "let x = 5;   \nconsole.log(x);\n"
    result = analyze_generic(code)
    assert any(i["rule_id"] == "trailing_whitespace" for i in result["issues"])


def test_detects_todo_marker():
    code = "// TODO: fix this later\nfunction f() {}\n"
    result = analyze_generic(code)
    assert any(i["rule_id"] == "todo_comment_left" for i in result["issues"])


def test_detects_deep_nesting():
    code = "\n".join(["    " * i + "if (true) {" for i in range(6)])
    result = analyze_generic(code)
    assert any(i["rule_id"] == "deep_nesting" for i in result["issues"])


def test_detects_long_file():
    code = "\n".join(["x = 1" for _ in range(500)])
    result = analyze_generic(code)
    assert any(i["rule_id"] == "file_too_long" for i in result["issues"])


def test_clean_code_has_no_issues():
    code = "function add(a, b) {\n    return a + b;\n}\n"
    result = analyze_generic(code)
    assert result["issues"] == []