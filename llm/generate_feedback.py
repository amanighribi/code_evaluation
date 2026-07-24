import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"


def build_prompt(issue_message: str, rubric: dict, code_snippet: str) -> str:
    rule_text = rubric.get("rule", "")
    why_it_matters = rubric.get("why_it_matters", "")
    good_example = rubric.get("good_example", "")
    tone_guidance = rubric.get("feedback_tone", "")

    prompt = f"""You are a supportive but rigorous programming teaching assistant giving feedback to a student on their code.

ISSUE DETECTED BY THE STATIC ANALYZER:
{issue_message}

RELEVANT RULE (from the course's pedagogical knowledge base):
{rule_text}

WHY THIS MATTERS:
{why_it_matters}

WHAT GOOD PRACTICE LOOKS LIKE:
{good_example}

TONE GUIDANCE FOR YOUR RESPONSE:
{tone_guidance}

STUDENT'S CODE (relevant excerpt):
```python
{code_snippet}
```

Write a short, specific feedback comment (3-5 sentences) for the student, addressing this exact issue in their code. Ground your explanation in the rule and rationale above. Do not simply restate the rule; explain it in context of their actual code. Be constructive, not harsh."""

    return prompt


def generate_feedback(issue_message: str, rubric: dict, code_snippet: str) -> str:
    prompt = build_prompt(issue_message, rubric, code_snippet)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=300,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Quick manual test
    from rag.retrieve import get_rubric_for_rule

    test_issue = "Function 'process' (line 3) is missing a docstring."
    test_rubric = get_rubric_for_rule("missing_docstring")
    test_code = """def process(data,flag,mode,extra,another_param):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            ...
    return result"""

    feedback = generate_feedback(test_issue, test_rubric, test_code)
    print("GENERATED FEEDBACK:\n")
    print(feedback)