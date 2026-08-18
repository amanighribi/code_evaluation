import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"


def build_evaluation_prompt(instructions, student_code, constraint_violations, test_results):
    violations_text = "None detected." if not constraint_violations else "\n".join(
        f"- {v['message']}" for v in constraint_violations
    )

    if test_results:
        passed = sum(1 for r in test_results if r["passed"])
        total = len(test_results)
        tests_text = f"{passed}/{total} test cases passed.\n"
        for r in test_results:
            if r.get("infra_error"):
                tests_text += f"- Test {r['test_number']}: COULD NOT RUN (infrastructure issue, not a code problem: {r['infra_error']}) - do not penalize the student for this.\n"
                continue
            status = "PASS" if r["passed"] else "FAIL"
            tests_text += f"- Test {r['test_number']}: {status} (input: {r['input']!r}, expected: {r['expected_output']!r}, got: {r['actual_output']!r})\n"
            if r.get("stderr"):
                tests_text += f"  Error: {r['stderr'][:200]}\n"
            if r.get("compile_error"):
                tests_text += f"  Compile error: {r['compile_error'][:200]}\n"
    else:
        tests_text = "No test cases were executed for this submission."

    prompt = (
        "You are an experienced programming instructor grading a student's exam submission.\n\n"
        "Respond in the SAME language as the exam instructions below (if the instructions are in French, respond in French; if in English, respond in English).\n\n"
        "EXAM INSTRUCTIONS:\n" + instructions + "\n\n"
        "STUDENT'S CODE:\n```\n" + student_code + "\n```\n\n"
        "CONSTRAINT VIOLATIONS (banned functions/imports detected by static analysis):\n" + violations_text + "\n\n"
        "ACTUAL TEST EXECUTION RESULTS (the code was run in a sandbox against real inputs):\n" + tests_text + "\n\n"
        "Using this evidence (constraint violations and REAL execution results, not just your reading of the code), "
        "evaluate this submission as a teacher would. Assess:\n"
        "1. Does the code correctly implement what the instructions ask for, based on the actual test results?\n"
        "2. Does the approach match what was required (e.g. was a specific algorithm genuinely implemented, or circumvented using a banned shortcut)?\n"
        "3. If tests failed, what does the error suggest about the bug?\n"
        "4. Overall assessment and constructive feedback for the student.\n\n"
        "Also propose a numeric grade out of 20, following typical French academic grading conventions, "
        "reflecting both correctness (based on real test results, not assumptions) and whether the required "
        "approach was genuinely followed (e.g. a correct answer obtained via a banned shortcut should be "
        "graded significantly lower than a genuine, correct implementation of the required approach).\n\n"
        "Respond ONLY with a valid JSON object, no other text before or after it, in this exact format:\n"
        '{"meets_requirements": "yes" | "partially" | "no", "grade_out_of_20": 0-20, '
        '"approach_assessment": "...", "correctness_notes": "...", "feedback": "..."}'
    )

    return prompt


def evaluate_submission(instructions, student_code, constraint_violations=None, test_results=None):
    constraint_violations = constraint_violations or []
    test_results = test_results or []

    prompt = build_evaluation_prompt(instructions, student_code, constraint_violations, test_results)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800,
    )

    raw_text = response.choices[0].message.content.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        grade = parsed.get("grade_out_of_20")
        if not isinstance(grade, (int, float)) or not (0 <= grade <= 20):
            parsed["grade_out_of_20"] = None  # invalid/out-of-range grade is safer than a wrong number
        return parsed
    except json.JSONDecodeError:
        return {
            "meets_requirements": "unknown",
            "grade_out_of_20": None,
            "approach_assessment": "",
            "correctness_notes": "",
            "feedback": "Could not parse evaluation response: " + raw_text[:300],
        }