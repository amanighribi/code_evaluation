from exam_mode.extract_constraints import extract_banned_names
from exam_mode.constraint_checker import check_constraints_multilang

instructions = """
Write a function bubble_sort(arr) that sorts a list of integers in ascending order
using the bubble sort algorithm. You must implement the sorting logic manually.
Do not use Python's built-in sort() or sorted() functions, and do not use any
external sorting libraries such as itertools.
"""

student_code = """
def bubble_sort(arr):
    return sorted(arr)
"""

print("Step 1: Extracting constraints from instructions...")
banned_names = extract_banned_names(instructions)
print(f"  Banned: {banned_names}\n")

print("Step 2: Checking student code against constraints...")
violations = check_constraints_multilang(student_code, banned_names, language="python")

if violations:
    print(f"  Found {len(violations)} violation(s):")
    for v in violations:
        print(f"   - {v['message']}")
else:
    print("  No constraint violations found.")