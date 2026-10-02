import os
import json
import re
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"

# Groq's on-demand tier for this model caps total tokens (prompt + completion) per request
# at a small number (the error we hit reported a limit of 8000). These budgets are kept well
# under that ceiling, since our token count is only an estimate, not an exact tokenizer count.
PROMPT_TOKEN_BUDGET = 3000     # max estimated tokens we'll pack into one request's prompt
MAX_COMPLETION_TOKENS = 4000   # hard ceiling on completion size for any single request
MIN_COMPLETION_TOKENS = 800
TOKENS_PER_ISSUE_COMPLETION = 350   # rough completion budget per issue in a batch
MAX_CODE_CHARS = 6000          # ~1500 estimated tokens; keeps a large file from dominating the budget

# Rate-limit handling. The limit tracked by Groq is per-minute, not per-request, so even
# individually well-sized batches can collide if sent back-to-back — this happened in
# practice: a second batch was rejected because an earlier batch's tokens hadn't cleared
# the window yet. Retrying respects the wait time Groq itself suggests; pacing batches
# apart reduces how often a retry is needed at all.
MAX_RATE_LIMIT_RETRIES = 3         # up to 4 total attempts per batch
DEFAULT_RETRY_DELAY_SECONDS = 2.0  # used when no wait hint can be parsed from the error
MAX_RETRY_WAIT_SECONDS = 5.0       # clamp: never block a request for longer than this per retry
INTER_BATCH_DELAY_SECONDS = 1.0    # pacing between successive batches of the same request

try:
    from groq import RateLimitError
except ImportError:  # different groq client versions may not expose this name the same way
    RateLimitError = None

_RETRY_AFTER_PATTERN = re.compile(r"try again in\s+([\d.]+)s", re.IGNORECASE)


def _estimate_tokens(text: str) -> int:
    """Rough, conservative estimate: ~4 characters per token. This is not an exact tokenizer
    count, only a safety margin to decide how to split requests before sending them."""
    return len(text) // 4 + 1


def _truncate_code_for_prompt(code: str, max_chars: int = MAX_CODE_CHARS) -> str:
    if len(code) <= max_chars:
        return code
    return (
        code[:max_chars]
        + "\n# ... (truncated for length; feedback below is based on the excerpt above) ..."
    )


def _format_issue_block(index: int, item: dict) -> str:
    issue = item["issue"]
    rubric = item["rubric"]
    return f"""
ISSUE {index} (rule_id: {item['rule_id']}):
Message: {issue}
Rule: {rubric.get('rule', '')}
Why it matters: {rubric.get('why_it_matters', '')}
Good practice example: {rubric.get('good_example', '')}
Tone guidance: {rubric.get('feedback_tone', '')}
"""


def _batch_issues(issues_with_rubrics: list, code_tokens: int) -> list:
    """Splits issues into batches sized so each batch's estimated prompt tokens (code
    repeated per batch + that batch's issue text) stays under PROMPT_TOKEN_BUDGET.
    A single issue whose rubric alone is too large still gets its own one-item batch
    rather than being dropped."""
    batches: list = []
    current: list = []
    current_tokens = code_tokens

    for item in issues_with_rubrics:
        item_text = _format_issue_block(len(current) + 1, item)
        item_tokens = _estimate_tokens(item_text)

        if current and current_tokens + item_tokens > PROMPT_TOKEN_BUDGET:
            batches.append(current)
            current = [item]
            current_tokens = code_tokens + item_tokens
        else:
            current.append(item)
            current_tokens += item_tokens

    if current:
        batches.append(current)

    return batches


def build_batch_prompt(issues_with_rubrics: list, code: str) -> str:
    issues_block = ""
    for i, item in enumerate(issues_with_rubrics, start=1):
        issues_block += _format_issue_block(i, item)

    prompt = f"""You are a supportive but rigorous programming teaching assistant giving feedback to a student on their code.

Below is the student's code, followed by a list of issues detected by a static analyzer, each with its relevant pedagogical rule.

STUDENT'S CODE:
```python
{code}
```

DETECTED ISSUES:
{issues_block}

For EACH issue above, provide two things:
1. "feedback": a short, specific explanation (2-4 sentences), grounded in the rule and rationale provided, referencing the actual code where relevant. Do not simply restate the rule.
2. "suggested_fix": a short, concrete corrected code snippet showing specifically how to fix THIS issue in THIS code (not a generic example). Keep it minimal — just the relevant lines, not the whole file. If a full working snippet isn't meaningful for this issue (e.g. a purely conceptual note), use an empty string.

Respond ONLY with a valid JSON array, with no other text before or after it, in this exact format:
[
  {{"rule_id": "...", "feedback": "...", "suggested_fix": "..."}},
  {{"rule_id": "...", "feedback": "...", "suggested_fix": "..."}}
]
There must be exactly {len(issues_with_rubrics)} entries in the array, one per issue, in the same order as listed above."""

    return prompt


def _fallback_entries(batch: list, reason: str) -> list:
    """Used whenever a batch's request fails outright after retries are exhausted. Keeps
    the pipeline returning a result instead of a 500, at the cost of that batch's issues
    getting a generic message instead of real feedback."""
    return [
        {
            "rule_id": item["rule_id"],
            "feedback": (
                "Automatic feedback for this issue could not be generated right now "
                f"({reason}). The issue itself is still valid — see the rule reference above, "
                "or try analyzing this file again in a moment."
            ),
            "suggested_fix": None,
        }
        for item in batch
    ]


def _is_rate_limit_error(exc: Exception) -> bool:
    if RateLimitError is not None and isinstance(exc, RateLimitError):
        return True
    if getattr(exc, "status_code", None) == 429:
        return True
    # Last resort, in case the installed groq client version doesn't expose either of the
    # above: match the phrasing actually seen from the API itself.
    text = str(exc)
    return "rate_limit_exceeded" in text or "Rate limit reached" in text


def _extract_retry_after_seconds(exc: Exception, default: float) -> float:
    """Prefers a structured Retry-After response header if the client exposes one; falls
    back to parsing Groq's own error message, which states a wait time directly
    (e.g. "Please try again in 1.7175s."); falls back to `default` if neither is present.
    Always clamped to MAX_RETRY_WAIT_SECONDS so a single retry can't block a request for long."""
    response = getattr(exc, "response", None)
    if response is not None:
        try:
            header_value = response.headers.get("retry-after")
        except Exception:
            header_value = None
        if header_value:
            try:
                return min(max(float(header_value), 0.1), MAX_RETRY_WAIT_SECONDS)
            except ValueError:
                pass

    match = _RETRY_AFTER_PATTERN.search(str(exc))
    if match:
        try:
            return min(max(float(match.group(1)), 0.1), MAX_RETRY_WAIT_SECONDS)
        except ValueError:
            pass

    return min(default, MAX_RETRY_WAIT_SECONDS)


def _call_llm_for_batch(batch: list, code: str) -> list:
    prompt = build_batch_prompt(batch, code)
    max_tokens = min(
        MAX_COMPLETION_TOKENS,
        max(MIN_COMPLETION_TOKENS, 400 + TOKENS_PER_ISSUE_COMPLETION * len(batch)),
    )

    total_attempts = MAX_RATE_LIMIT_RETRIES + 1
    response = None

    for attempt in range(total_attempts):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=max_tokens,
            )
            break  # success
        except Exception as e:
            is_last_attempt = attempt == total_attempts - 1
            if _is_rate_limit_error(e) and not is_last_attempt:
                wait_seconds = _extract_retry_after_seconds(e, DEFAULT_RETRY_DELAY_SECONDS)
                print(
                    f"WARNING: rate limited on a batch of {len(batch)} issue(s) "
                    f"(attempt {attempt + 1}/{total_attempts}); retrying in {wait_seconds:.1f}s: {e!r}"
                )
                time.sleep(wait_seconds)
                continue

            reason = (
                "the AI service is still rate-limited after several retries"
                if _is_rate_limit_error(e)
                else "the AI service is temporarily unavailable"
            )
            print(
                f"WARNING: LLM call failed for a batch of {len(batch)} issue(s) "
                f"after {attempt + 1} attempt(s): {e!r}"
            )
            return _fallback_entries(batch, reason)

    raw_text = response.choices[0].message.content.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        feedback_list = json.loads(raw_text)
    except json.JSONDecodeError:
        print(f"WARNING: JSON parse failed, response length was {len(raw_text)} chars. Truncated response:\n{raw_text[-300:]}")
        return _fallback_entries(batch, "the response could not be parsed")

    return feedback_list


def generate_batch_feedback(issues_with_rubrics: list, code: str) -> list:
    """Takes a list of {rule_id, issue, rubric} dicts and the full code.
    Returns a list of {rule_id, feedback, suggested_fix} dicts, one per input issue.

    Large files or issue lists are split into several smaller requests to stay under
    the LLM provider's per-request token limit. Successive batches are paced with a
    short delay so they don't collide with the provider's per-minute rate limit, and
    any batch that still hits a rate limit retries with backoff before falling back
    to a generic per-issue message — this function never raises to its caller."""
    if not issues_with_rubrics:
        return []

    code_for_prompt = _truncate_code_for_prompt(code)
    code_tokens = _estimate_tokens(code_for_prompt)

    batches = _batch_issues(issues_with_rubrics, code_tokens)

    all_feedback = []
    for i, batch in enumerate(batches):
        if i > 0:
            time.sleep(INTER_BATCH_DELAY_SECONDS)
        all_feedback.extend(_call_llm_for_batch(batch, code_for_prompt))

    return all_feedback


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

    print(f"Sending {len(issues_with_rubrics)} issue(s), split into paced batches as needed...\n")
    feedback_list = generate_batch_feedback(issues_with_rubrics, code)

    for entry in feedback_list:
        print(f"[{entry.get('rule_id')}]")
        print("FEEDBACK:", entry.get("feedback"))
        print("SUGGESTED_FIX:", repr(entry.get("suggested_fix")))
        print("-" * 70)