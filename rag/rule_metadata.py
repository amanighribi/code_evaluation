import os
import json

RUBRICS_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "rubrics.json")

_cache = None


def _load_rules():
    global _cache
    if _cache is None:
        with open(RUBRICS_FILE, "r", encoding="utf-8") as f:
            rules = json.load(f)
        _cache = {rule["rule_id"]: rule for rule in rules}
    return _cache


def get_severity(rule_id: str) -> str:
    """Returns 'critical' | 'major' | 'minor' | 'info', or 'unknown' if the rule isn't found."""
    rules = _load_rules()
    rule = rules.get(rule_id)
    return rule.get("severity", "unknown") if rule else "unknown"


SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "info": 3, "unknown": 4}


def sort_by_severity(issues: list) -> list:
    """Sorts a list of issue dicts (each with a 'severity' key) from most to least severe."""
    return sorted(issues, key=lambda i: SEVERITY_ORDER.get(i.get("severity", "unknown"), 4))


if __name__ == "__main__":
    print(get_severity("bare_except"))
    print(get_severity("missing_docstring"))
    print(get_severity("nonexistent_rule"))