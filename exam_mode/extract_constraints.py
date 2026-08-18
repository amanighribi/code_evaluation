import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"


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


def extract_exam_metadata(instructions: str) -> dict:
    """Returns {"banned_names": [...], "test_cases": [...]} extracted from free-text exam instructions."""
    prompt = build_extraction_prompt(instructions)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
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
        return {
            "banned_names": parsed.get("banned_names", []),
            "test_cases": parsed.get("test_cases", []),
        }
    except json.JSONDecodeError:
        print(f"Warning: could not parse extraction response: {raw_text[:200]}")
        return {"banned_names": [], "test_cases": []}


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