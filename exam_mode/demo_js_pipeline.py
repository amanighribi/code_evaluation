from exam_mode.full_exam_pipeline import run_full_exam_evaluation
import json

instructions = """
Write a JavaScript program that reads two integers from stdin (one per line)
and prints their sum. Do not use eval().

For example, given the input 3 and 4, the output should be: 7
"""

student_code = """
const lines = require('fs').readFileSync('/dev/stdin', 'utf8').split('\\n');
const a = parseInt(lines[0]);
const b = parseInt(lines[1]);
console.log(a + b);
"""

result = run_full_exam_evaluation(instructions, student_code, language="javascript")
print(json.dumps(result, indent=2, ensure_ascii=False))