from exam_mode.extract_constraints import extract_exam_metadata
import json

instructions = """
Write a program that reads an integer n, then a list of n integers, and prints
them sorted in ascending order using the bubble sort algorithm. Do not use
sort() or sorted().

Examples:
- Given n=5 and the list [5, 2, 4, 1, 3], the output should be: 1 2 3 4 5
- Given n=3 and the list [10, -1, 4], the output should be: -1 4 10
- Given n=1 and the list [42], the output should be: 42
"""

metadata = extract_exam_metadata(instructions)
print(json.dumps(metadata, indent=2, ensure_ascii=False))