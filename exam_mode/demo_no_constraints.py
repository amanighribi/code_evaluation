from exam_mode.full_exam_pipeline import run_full_exam_evaluation
import json

instructions = """
Write a function factorial(n) that computes the factorial of a non-negative integer n.
"""

student_code = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""

result = run_full_exam_evaluation(instructions, student_code, language="python")
print(json.dumps(result, indent=2, ensure_ascii=False))