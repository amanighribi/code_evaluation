import json
from static_analysis.analyzer import analyze_code
from rag.retrieve import get_rubric_for_rule

with open("samples/sample_student_code.py") as f:
    code = f.read()

result = analyze_code(code)

print(f"Found {len(result['issues'])} issues.\n")

for issue in result["issues"]:
    rule_id = issue["rule_id"]
    message = issue["message"]
    rubric = get_rubric_for_rule(rule_id)

    print("=" * 70)
    print(f"ISSUE: {message}")
    print(f"RULE: {rule_id}")
    if rubric:
        print(f"WHY IT MATTERS: {rubric.get('why_it_matters', '')[:200]}...")
    print()