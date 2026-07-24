import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"


def build_extraction_prompt(instructions: str) -> str:
    return f"""You are helping process a programming exam statement written by an instructor.

EXAM INSTRUCTIONS:
{instructions}

Your task: identify any explicitly banned functions, methods, or modules/imports mentioned in these instructions (e.g. "do not use sort()" means "sort" is banned).

Only include names that are EXPLICITLY forbidden in the text. Do not guess or add anything not clearly stated. If nothing is explicitly banned, return an empty list.

Respond ONLY with a valid JSON object, no other text before or after it, in this exact format:
{{"banned_names": ["name1", "name2"]}}

If there are no banned names, respond with:
{{"banned_names": []}}"""


def extract_banned_names(instructions: str) -> list[str]:
    prompt = build_extraction_prompt(instructions)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=300,
    )

    raw_text = response.choices[0].message.content.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        return parsed.get("banned_names", [])
    except json.JSONDecodeError:
        print(f"Warning: could not parse constraint extraction response: {raw_text[:200]}")
        return []


if __name__ == "__main__":
    test_instructions = """
    Write a function bubble_sort(arr) that sorts a list of integers in ascending order
    using the bubble sort algorithm. You must implement the sorting logic manually.
    Do not use Python's built-in sort() or sorted() functions, and do not use any
    external sorting libraries such as itertools.
    """

    banned = extract_banned_names(test_instructions)
    print("Extracted banned names:", banned)