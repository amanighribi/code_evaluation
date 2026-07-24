import json
from static_analysis.analyzer import analyze_code
from rag.retrieve import get_rubric_for_rule
from llm.generate_feedback import generate_feedback

with open("samples/sample_student_code.py") as f:
    code = f.read()

result = analyze_code(code)

print(f"Analyzing {len(result['issues'])} issues...\n")

report = []

for issue in result["issues"]:
    rule_id = issue["rule_id"]
    message = issue["message"]
    rubric = get_rubric_for_rule(rule_id)

    print(f"Generating feedback for: {message}")
    feedback_text = generate_feedback(message, rubric, code)

    report.append({
        "rule_id": rule_id,
        "issue": message,
        "feedback": feedback_text,
    })

print("\n" + "=" * 70)
print("FULL FEEDBACK REPORT")
print("=" * 70)

for entry in report:
    print(f"\n[{entry['rule_id']}]")
    print(f"Issue: {entry['issue']}")
    print(f"Feedback: {entry['feedback']}\n")
    print("-" * 70)

with open("feedback_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(f"\nSaved {len(report)} feedback entries to feedback_report.json")