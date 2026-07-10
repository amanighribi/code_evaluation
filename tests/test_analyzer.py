from static_analysis.analyzer import analyze_code


def test_detects_missing_docstring():
    code = "def foo():\n    return 1\n"
    result = analyze_code(code)
    assert any("missing a docstring" in issue for issue in result["issues"])


def test_detects_too_many_parameters():
    code = "def foo(a, b, c, d, e):\n    return a\n"
    result = analyze_code(code)
    assert any("too many parameters" in issue for issue in result["issues"])


def test_detects_high_complexity():
    code = """
def foo(x):
    if x > 0:
        if x > 1:
            if x > 2:
                if x > 3:
                    if x > 4:
                        if x > 5:
                            return 1
    return 0
"""
    result = analyze_code(code)
    assert any("high cyclomatic complexity" in issue for issue in result["issues"])


def test_detects_bad_class_naming():
    code = "class myclass:\n    pass\n"
    result = analyze_code(code)
    assert any("PascalCase" in issue for issue in result["issues"])


def test_clean_code_has_no_issues():
    code = '''def add(a, b):
    """Add two numbers."""
    return a + b
'''
    result = analyze_code(code)
    assert result["issues"] == []


def test_counts_functions_and_classes():
    code = """
def foo():
    pass

class Bar:
    def method(self):
        pass
"""
    result = analyze_code(code)
    assert result["num_functions"] == 2
    assert result["num_classes"] == 1

def test_detects_unused_import():
    code = "import os\n\ndef foo():\n    return 1\n"
    result = analyze_code(code)
    assert any("unused" in issue for issue in result["issues"])


def test_detects_bare_except():
    code = """
def foo():
    try:
        pass
    except:
        pass
"""
    result = analyze_code(code)
    assert any("Bare 'except:'" in issue for issue in result["issues"])


def test_detects_magic_number():
    code = "def foo(x):\n    if x > 42:\n        return True\n"
    result = analyze_code(code)
    assert any("Magic number" in issue for issue in result["issues"])


def test_detects_unused_variable():
    code = "def foo():\n    x = 5\n    return 1\n"
    result = analyze_code(code)
    assert any("assigned but never used" in issue for issue in result["issues"])


def test_detects_duplicate_functions():
    code = """
def foo(a, b):
    return a + b

def bar(a, b):
    return a + b
"""
    result = analyze_code(code)
    assert any("duplicate" in issue for issue in result["issues"])