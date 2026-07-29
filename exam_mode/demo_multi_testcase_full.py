from exam_mode.full_exam_pipeline import run_full_exam_evaluation
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

correct_code = """
n = int(input())
arr = list(map(int, input().split()))
for i in range(n):
    for j in range(0, n - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
print(' '.join(map(str, arr)))
"""

result = run_full_exam_evaluation(instructions, correct_code, language="python")
print(json.dumps(result, indent=2, ensure_ascii=False))