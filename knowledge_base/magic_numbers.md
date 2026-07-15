\---

rule\_id: magic\_number

category: readability

severity: minor

source: "Clean Code (Robert C. Martin) — avoid magic numbers"

analyzer\_check: "hardcoded numeric literal in comparison, excluding 0/1/-1"

\---



\# Magic Number



\## Rule

Hardcoded numeric literals used in conditions (e.g. `if age > 65`) should generally be replaced with a named constant explaining what the number represents.



\## Why it matters

`if x > 42` gives no indication of \*why\* 42 is meaningful. `if x > MAX\_RETRIES` is self-explanatory and easier to update consistently if the value ever needs to change.



\## What good looks like

```python

MAX\_RETRIES = 3

if attempts > MAX\_RETRIES:

&#x20;   ...

```



\## Common student mistake

Using the same magic number in multiple places, making it error-prone to update consistently later.



\## Feedback tone guidance for LLM

Suggest a plausible constant name based on context if possible, not just "use a constant."

