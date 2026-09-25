import os
import re
import json

MODEL = "openai/gpt-oss-120b"

_client = None


def _get_client():
    """Lazy so that importing this module (e.g. for the deterministic extractors) needs no API key."""
    global _client
    if _client is None:
        from dotenv import load_dotenv
        from groq import Groq
        load_dotenv()
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client


# ---------------------------------------------------------------------------
# 0. PDF text cleanup
# ---------------------------------------------------------------------------
def clean_pdf_text(text: str) -> str:
    """Removes page-break artefacts that split sentences in the middle
    (form feeds, 'n/N' page footers, stray '-' bullets left by the layout)."""
    text = text.replace("\f", "\n")
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.fullmatch(r"\d+\s*/\s*\d+", stripped):  # page footer such as "2/3"
            continue
        if stripped in {"-", "•", "–"}:  # orphan bullet marker
            continue
        lines.append(line)
    return "\n".join(lines)


def _squash(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# 1. Deterministic extractors (no LLM: cheap, reproducible, cannot hallucinate)
# ---------------------------------------------------------------------------
_SIGNATURE_RE = re.compile(
    r"public\s+(?P<ret>[\w<>\[\],.?]+(?:\s*<[^>]*>)?)\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*;"
)


def extract_required_signatures(instructions: str) -> list:
    """Java method signatures the exam imposes, e.g.
    {'name': 'ajouterVirement', 'return_type': 'String', 'params': ['Transaction transaction']}"""
    text = _squash(clean_pdf_text(instructions))
    found, seen = [], set()
    for m in _SIGNATURE_RE.finditer(text):
        ret = _squash(m.group("ret"))
        params = [_squash(p) for p in m.group("params").split(",") if p.strip()]
        key = (m.group("name"), tuple(params))
        if key in seen:
            continue
        seen.add(key)
        found.append({"name": m.group("name"), "return_type": ret, "params": params})
    return found


def extract_required_messages(instructions: str) -> list:
    """Exact messages the exam says a method must return, quoted with « ... »."""
    text = clean_pdf_text(instructions)
    messages = []
    for m in re.finditer(r"«(.+?)»", text, flags=re.DOTALL):
        msg = _squash(m.group(1))
        # skip diagram stereotypes («enum») and short quoted tokens («get»)
        if len(msg) >= 12 and " " in msg and msg.lower() != "enum":
            messages.append(msg)
    return messages


# ---------------------------------------------------------------------------
# 2. LLM extraction (banned names + explicit stdin/stdout examples)
# ---------------------------------------------------------------------------
def build_extraction_prompt(instructions: str) -> str:
    return f"""You are helping process a programming exam statement written by an instructor.

EXAM INSTRUCTIONS:
{instructions}

Your task has two parts:

PART 1 - Banned names: identify any explicitly banned functions, methods, or modules/imports mentioned (e.g. "do not use sort()" means "sort" is banned). Only include names EXPLICITLY forbidden. Return bare identifier names only, WITHOUT parentheses (e.g. "sort", not "sort()"). If nothing is banned, return an empty list.

PART 2 - Test cases: identify any example input/output pairs given in the instructions (e.g. "for example, given [5,2,4,1,3] the output should be [1,2,3,4,5]"). Convert each example into a stdin/stdout format matching how the program is expected to read input and print output, based on the instructions (e.g. if the program should read a count n then n integers on separate lines, format the input that way). If no explicit examples are given, return an empty list. Do not invent test cases that are not implied by the instructions.

Respond ONLY with a valid JSON object, no other text before or after it, in this exact format:
{{
  "banned_names": ["name1", "name2"],
  "test_cases": [
    {{"input": "5\\n5 2 4 1 3", "expected_output": "1 2 3 4 5"}}
  ]
}}

If there are no banned names or no test cases, use empty lists for those fields."""


def _call_llm(instructions: str) -> dict:
    """Raises on any failure so the caller can report it instead of silently returning empty lists."""
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": build_extraction_prompt(instructions)}],
        temperature=0.0,
        # gpt-oss-120b is a reasoning model: reasoning tokens count against this budget,
        # so 800 could be consumed entirely before any JSON is emitted.
        max_tokens=4096,
    )
    raw_text = (response.choices[0].message.content or "").strip()
    if not raw_text:
        raise ValueError("empty response from model (likely truncated by max_tokens)")

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    parsed = json.loads(raw_text)
    return {
        "banned_names": parsed.get("banned_names", []) or [],
        "test_cases": parsed.get("test_cases", []) or [],
    }


def extract_exam_metadata(instructions: str) -> dict:
    """Returns the extracted metadata. Keys:
      banned_names, test_cases                 (as before; test_cases are stdin/stdout pairs)
      required_signatures, required_messages   (deterministic, for Java/Spring style exams)
      exam_kind                                'stdin_stdout' | 'service_api'
      tests_available                          True only if there is something executable to run
      extraction_status / extraction_error     'ok' or 'failed' (LLM step) so failures are never silent
    """
    cleaned = clean_pdf_text(instructions)
    signatures = extract_required_signatures(cleaned)
    messages = extract_required_messages(cleaned)

    banned, test_cases, status, error = [], [], "ok", None
    try:
        llm = _call_llm(cleaned)
        banned, test_cases = llm["banned_names"], llm["test_cases"]
    except Exception as exc:  # noqa: BLE001 - deliberate: report, don't hide
        status, error = "failed", f"{type(exc).__name__}: {exc}"
        print(f"Warning: LLM extraction failed: {error}")

    exam_kind = "service_api" if signatures and not test_cases else "stdin_stdout"
    return {
        "banned_names": banned,
        "test_cases": test_cases,
        "required_signatures": signatures,
        "required_messages": messages,
        "exam_kind": exam_kind,
        "tests_available": bool(test_cases),
        "extraction_status": status,
        "extraction_error": error,
    }


# Kept for backward compatibility with any existing code calling the old function name
def extract_banned_names(instructions: str) -> list:
    return extract_exam_metadata(instructions)["banned_names"]


if __name__ == "__main__":
    test_instructions = """
    Write a program that reads an integer n, then a list of n integers, and prints
    them sorted in ascending order using the bubble sort algorithm. Do not use
    Python's built-in sort() or sorted() functions.

    For example, given n=5 and the list [5, 2, 4, 1, 3], the output should be:
    1 2 3 4 5
    """

    metadata = extract_exam_metadata(test_instructions)
    print("Banned names:", metadata["banned_names"])
    print("Test cases:", metadata["test_cases"])