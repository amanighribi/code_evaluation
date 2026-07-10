import json
from static_analysis.analyzer import analyze_code

with open("samples/sample_student_code.py") as f:
    code = f.read()

result = analyze_code(code)
print(json.dumps(result, indent=2))