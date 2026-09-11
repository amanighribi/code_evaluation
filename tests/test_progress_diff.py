from progress.diff import compute_quality_score, compare_submissions, _issue_signature


def make_issue(rule_id, message, severity):
    return {"rule_id": rule_id, "message": message, "severity": severity}


def test_quality_score_weights_by_severity():
    issues = [
        make_issue("bare_except", "msg1", "critical"),
        make_issue("magic_number", "msg2", "minor"),
    ]
    assert compute_quality_score(issues) == 4 + 2


def test_quality_score_empty_is_zero():
    assert compute_quality_score([]) == 0


def test_issue_signature_matches_same_issue():
    a = make_issue("bare_except", "Bare except at line 5.", "critical")
    b = make_issue("bare_except", "Bare except at line 5.", "critical")
    assert _issue_signature(a) == _issue_signature(b)


def test_detects_resolved_issue():
    previous = [make_issue("bare_except", "msg1", "critical")]
    current = []
    result = compare_submissions(previous, current)
    assert result["resolved_count"] == 1
    assert result["new_count"] == 0
    assert result["trend"] == "improved"


def test_detects_new_issue():
    previous = []
    current = [make_issue("magic_number", "msg2", "minor")]
    result = compare_submissions(previous, current)
    assert result["new_count"] == 1
    assert result["resolved_count"] == 0
    assert result["trend"] == "regressed"


def test_detects_persisting_issue():
    issue = make_issue("missing_docstring", "msg3", "info")
    previous = [issue]
    current = [issue]
    result = compare_submissions(previous, current)
    assert result["persisting_count"] == 1
    assert result["resolved_count"] == 0
    assert result["new_count"] == 0
    assert result["trend"] == "unchanged"


def test_trend_improved_even_with_new_minor_issue_if_critical_resolved():
    previous = [make_issue("bare_except", "msg1", "critical")]
    current = [make_issue("magic_number", "msg2", "minor")]
    result = compare_submissions(previous, current)
    assert result["trend"] == "improved"
    assert result["previous_quality_score"] == 4
    assert result["current_quality_score"] == 2