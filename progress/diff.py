SEVERITY_WEIGHT = {"critical": 4, "major": 3, "minor": 2, "info": 1, "unknown": 1}


def compute_quality_score(issues: list) -> int:
    """Lower is better. Sum of severity weights across all issues."""
    return sum(SEVERITY_WEIGHT.get(issue.get("severity", "unknown"), 1) for issue in issues)


def _issue_signature(issue: dict) -> str:
    """A stable identity for one issue, used to match the 'same' issue across submissions.
    Based on rule_id + message, since exact line numbers can shift with unrelated edits."""
    return f"{issue.get('rule_id')}::{issue.get('message')}"


def compare_submissions(previous_issues: list, current_issues: list) -> dict:
    """Compares two sets of issues and classifies what changed between them."""
    prev_signatures = {_issue_signature(i) for i in previous_issues}
    curr_signatures = {_issue_signature(i) for i in current_issues}

    resolved_sigs = prev_signatures - curr_signatures
    new_sigs = curr_signatures - prev_signatures
    persisting_sigs = prev_signatures & curr_signatures

    resolved = [i for i in previous_issues if _issue_signature(i) in resolved_sigs]
    new = [i for i in current_issues if _issue_signature(i) in new_sigs]
    persisting = [i for i in current_issues if _issue_signature(i) in persisting_sigs]

    prev_score = compute_quality_score(previous_issues)
    curr_score = compute_quality_score(current_issues)

    if curr_score < prev_score:
        trend = "improved"
    elif curr_score > prev_score:
        trend = "regressed"
    else:
        trend = "unchanged"

    return {
        "trend": trend,
        "previous_quality_score": prev_score,
        "current_quality_score": curr_score,
        "resolved_issues": resolved,
        "new_issues": new,
        "persisting_issues": persisting,
        "resolved_count": len(resolved),
        "new_count": len(new),
        "persisting_count": len(persisting),
    }


if __name__ == "__main__":
    previous = [
        {"rule_id": "missing_docstring", "message": "Function 'foo' is missing a docstring.", "severity": "info"},
        {"rule_id": "bare_except", "message": "Bare except at line 5.", "severity": "critical"},
        {"rule_id": "unused_import", "message": "Import 'os' is unused.", "severity": "info"},
    ]
    current = [
        {"rule_id": "missing_docstring", "message": "Function 'foo' is missing a docstring.", "severity": "info"},
        {"rule_id": "magic_number", "message": "Magic number 7 at line 10.", "severity": "minor"},
    ]

    import json
    print(json.dumps(compare_submissions(previous, current), indent=2))