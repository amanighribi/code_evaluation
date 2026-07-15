\---

rule\_id: naming\_convention\_violation

category: readability

severity: minor

source: "PEP 8 — Style Guide for Python Code"

analyzer\_check: "function not snake\_case OR class not PascalCase"

\---



\# Naming Convention Violation



\## Rule

Python convention (PEP 8) requires function and variable names in `snake\_case`, and class names in `PascalCase`.



\## Why it matters

Consistent naming makes code instantly recognizable — seeing `PascalCase` tells a reader "this is a class" without needing more context. Violating convention creates friction for anyone reading or reviewing the code, including graders.



\## What good looks like

```python

class StudentRecord:      # PascalCase for classes

&#x20;   def calculate\_gpa(self):  # snake\_case for functions

&#x20;       ...

```



\## Common student mistake

Using `camelCase` (common in Java/JavaScript) out of habit, or all-uppercase method names.



\## Feedback tone guidance for LLM

Note that this is a convention (not a functional bug), but explain that following it matters for team readability and tooling consistency.

