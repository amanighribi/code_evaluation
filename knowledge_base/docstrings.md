\---

rule\_id: missing\_docstring

category: documentation

severity: minor

source: "PEP 257 – Docstring Conventions"

analyzer\_check: "has\_docstring == false"

\---



\# Missing Docstring



\## Rule

Every function and class should have a docstring explaining what it does, its parameters, and what it returns, unless the function is trivially self-explanatory (e.g. a one-line getter).



\## Why it matters

Docstrings are the first thing a reader — a teammate, a grader, or your future self — checks to understand a function's purpose without reading its full implementation. In collaborative and academic settings, undocumented code significantly increases the time needed to review, maintain, or extend it. PEP 257 establishes docstrings as a core Python convention, not an optional nicety.



\## What good looks like

```python

def calculate\_average(grades: list\[float]) -> float:

&#x20;   """Return the arithmetic mean of a list of grades.



&#x20;   Args:

&#x20;       grades: A list of numeric grade values.



&#x20;   Returns:

&#x20;       The average grade as a float.

&#x20;   """

&#x20;   return sum(grades) / len(grades)

```



\## Common student mistake

Writing a docstring that just restates the function name (e.g. `"""Calculates average."""` with no mention of parameters or return value) provides little more value than no docstring at all.



\## Feedback tone guidance for LLM

Explain \*why\* the docstring matters for this specific function, not just that one is missing. If the function is complex, emphasize that the docstring reduces cognitive load for readers.

