import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"


def build_batch_prompt(issues_with_rubrics: list, code: str) -> str:
    issues_block = ""
    for i, item in enumerate(issues_with_rubrics, start=1):
        issue = item["issue"]
        rubric = item["rubric"]
        issues_block += f"""
ISSUE {i} (rule_id: {item['rule_id']}):
Message: {issue}
Rule: {rubric.get('rule', '')}
Why it matters: {rubric.get('why_it_matters', '')}
Good practice example: {rubric.get('good_example', '')}
Tone guidance: {rubric.get('feedback_tone', '')}
"""

    prompt = f"""You are a supportive but rigorous programming teaching assistant giving feedback to a student on their code.

Below is the student's code, followed by a list of issues detected by a static analyzer, each with its relevant pedagogical rule.

STUDENT'S CODE:
```python
{code}
```

DETECTED ISSUES:
{issues_block}

For EACH issue above, write a short, specific feedback comment (2-4 sentences), grounded in the rule and rationale provided, referencing the actual code where relevant. Do not simply restate the rule.

Respond ONLY with a valid JSON array, with no other text before or after it, in this exact format:
[
  {{"rule_id": "...", "feedback": "..."}},
  {{"rule_id": "...", "feedback": "..."}}
]

There must be exactly {len(issues_with_rubrics)} entries in the array, one per issue, in the same order as listed above."""

    return prompt


def generate_batch_feedback(issues_with_rubrics: list, code: str) -> list:
    """Takes a list of {rule_id, issue, rubric} dicts and the full code.
    Returns a list of {rule_id, feedback} dicts."""
    if not issues_with_rubrics:
        return []

    prompt = build_batch_prompt(issues_with_rubrics, code)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000,
    )

    raw_text = response.choices[0].message.content.strip()

    # Defensive parsing: strip markdown code fences if the model adds them anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        feedback_list = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback: return the raw text as a single error entry so the pipeline doesn't crash
        return [{"rule_id": "parse_error", "feedback": f"Could not parse LLM response: {raw_text[:300]}"}]

    return feedback_list


if __name__ == "__main__":
    from rag.retrieve import get_rubric_for_rule
    from static_analysis.analyzer import analyze_code

    with open("samples/sample_student_code.py") as f:
        code = f.read()

    result = analyze_code(code)

    issues_with_rubrics = []
    for issue in result["issues"]:
        rule_id = issue["rule_id"]
        rubric = get_rubric_for_rule(rule_id)
        issues_with_rubrics.append({
            "rule_id": rule_id,
            "issue": issue["message"],
            "rubric": rubric,
        })

    print(f"Sending {len(issues_with_rubrics)} issues in a single batched request...\n")
    feedback_list = generate_batch_feedback(issues_with_rubrics, code)

    for entry in feedback_list:
        print(f"[{entry.get('rule_id')}]")
        print(entry.get("feedback"))
        print("-" * 70)