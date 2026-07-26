from exam_mode.sandbox_executor import run_python_in_sandbox

code = """
n = int(input())
arr = list(map(int, input().split()))
arr.sort()
print(' '.join(map(str, arr)))
"""

result = run_python_in_sandbox(code, stdin_input="5\n5 2 4 1 3", timeout=10)
print(result)