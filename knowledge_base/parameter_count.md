\---

rule\_id: too\_many\_parameters

category: design

severity: minor

source: "Clean Code (Robert C. Martin) — function argument guidelines"

analyzer\_check: "num\_params > 4"

\---



\# Too Many Parameters



\## Rule

A function should ideally take 0-3 parameters. More than 4 is a signal the function may be doing too much or that related parameters should be grouped into an object/dataclass.



\## Why it matters

Functions with many parameters are hard to call correctly (easy to mix up argument order), hard to test (many combinations), and often indicate the function has too many responsibilities.



\## What good looks like

```python

def create\_student(name, age, major):  # 3 params, fine

&#x20;   ...



\# Instead of 6 loose parameters, group related data:

def create\_student(profile: StudentProfile):

&#x20;   ...

```



\## Common student mistake

Adding a new parameter every time a function needs "one more piece of data" rather than reconsidering the function's design.



\## Feedback tone guidance for LLM

Suggest grouping related parameters (e.g. into a dict or class) rather than just saying "reduce parameters" — give a concrete regrouping idea if possible.

