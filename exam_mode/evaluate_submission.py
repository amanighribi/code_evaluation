import os
import json
import re

MODEL = "openai/gpt-oss-120b"

_client = None


def _get_client():
    global _client
    if _client is None:
        from dotenv import load_dotenv
        from groq import Groq
        load_dotenv()
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client


_FR = {"le", "la", "les", "des", "du", "de", "un", "une", "et", "est", "sur", "pour", "dans", "que", "qui", "avec", "au", "aux", "par", "ne", "pas"}
_EN = {"the", "and", "is", "of", "to", "in", "for", "with", "that", "this", "are", "be", "on", "by"}


def _output_language(instructions: str) -> str:
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", instructions.lower())
    return "French" if sum(w in _FR for w in words) > sum(w in _EN for w in words) else "English"


def build_evaluation_prompt(instructions, student_code, constraint_violations, test_results, static_results=None):
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
        tests_text = "NO test was executed for this submission. Functional correctness has NOT been verified by execution."

    static_block = ""
    if static_results and static_results.get("checks"):
        from exam_mode.java_static_checks import render_evidence_for_prompt
        static_block = render_evidence_for_prompt(static_results) + "\n\n"

    language = _output_language(instructions)

    prompt = (
        "You are an experienced programming instructor grading a student's exam submission.\n\n"
        f"Write ALL text fields of your answer in {language} (the language of the exam instructions).\n\n"
        "EXAM INSTRUCTIONS:\n" + instructions + "\n\n"
        "STUDENT'S CODE:\n```\n" + student_code + "\n```\n\n"
        "CONSTRAINT VIOLATIONS (banned functions/imports detected by static analysis):\n" + violations_text + "\n\n"
        + static_block +
        "TEST EXECUTION RESULTS:\n" + tests_text + "\n\n"
        "Evaluate this submission as a teacher would. Base every claim on the verified facts above, on real test "
        "results, or on code you can point to. If you suspect a defect that you cannot demonstrate from the code, "
        "say it is UNVERIFIED instead of stating it as fact. Never recommend a change that contradicts the exam's "
        "class diagram. Assess:\n"
        "1. Does the code implement what the instructions ask for?\n"
        "2. Does the approach match what was required?\n"
        "3. If tests failed, what does the error suggest about the bug?\n"
        "4. Overall assessment and constructive feedback for the student.\n\n"
        "GRADING: if the exam states points per question (e.g. '(/1.5)', '(6 points)'), use exactly that scheme: "
        "one entry per graded item in points_breakdown, max_points taken from the exam, all max_points adding up to 20. "
        "Award partial points where justified. If the exam gives no point scheme, return an empty points_breakdown "
        "and estimate grade_out_of_20 following French academic conventions. If nothing was executed, do not award "
        "full points for behaviour you could not verify.\n\n"
        "Respond ONLY with a valid JSON object, no other text before or after it, in this exact format:\n"
        '{"meets_requirements": "yes" | "partially" | "no", "grade_out_of_20": 0-20, '
        '"points_breakdown": [{"item": "...", "max_points": 0, "awarded_points": 0, "justification": "..."}], '
        '"approach_assessment": "...", "correctness_notes": "...", "feedback": "..."}'
    )

    return prompt


def _validated_breakdown(parsed: dict):
    """Returns a clean breakdown, or None if it is missing/inconsistent (never trust a sum the model wrote)."""
    bd = parsed.get("points_breakdown")
    if not isinstance(bd, list) or not bd:
        return None
    clean = []
    for item in bd:
        try:
            mx, aw = float(item["max_points"]), float(item["awarded_points"])
        except (KeyError, TypeError, ValueError):
            return None
        if mx < 0 or aw < 0 or aw > mx:
            return None
        clean.append({"item": str(item.get("item", "")), "max_points": mx, "awarded_points": aw,
                      "justification": str(item.get("justification", ""))})
    if abs(sum(i["max_points"] for i in clean) - 20) > 0.01:
        return None
    return clean


def evaluate_submission(instructions, student_code, constraint_violations=None, test_results=None, static_results=None):
    constraint_violations = constraint_violations or []
    test_results = test_results or []

    prompt = build_evaluation_prompt(instructions, student_code, constraint_violations, test_results, static_results)

    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,      # was 0.3: sampling noise alone can move a grade by several points
        max_tokens=6000,      # gpt-oss-120b reasoning tokens count against this; 2500 risks a truncated, unparsable answer
    )

    raw_text = (response.choices[0].message.content or "").strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "meets_requirements": "unknown",
            "grade_out_of_20": None,
            "grade_source": None,
            "points_breakdown": [],
            "approach_assessment": "",
            "correctness_notes": "",
            "feedback": "Could not parse evaluation response: " + raw_text[:300],
        }

    breakdown = _validated_breakdown(parsed)
    if breakdown:
        # The grade is computed here from the itemised points, not taken from the model's own total.
        parsed["points_breakdown"] = breakdown
        parsed["grade_out_of_20"] = round(sum(i["awarded_points"] for i in breakdown), 2)
        parsed["grade_source"] = "points_breakdown"
    else:
        parsed["points_breakdown"] = []
        grade = parsed.get("grade_out_of_20")
        if not isinstance(grade, (int, float)) or isinstance(grade, bool) or not (0 <= grade <= 20):
            parsed["grade_out_of_20"] = None  # invalid/out-of-range grade is safer than a wrong number
        parsed["grade_source"] = "model_estimate"
    return parsed