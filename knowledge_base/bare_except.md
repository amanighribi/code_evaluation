\---

rule\_id: bare\_except

category: correctness

severity: major

source: "PEP 8 — 'bare except' clauses should be avoided"

analyzer\_check: "except: with no exception type"

\---



\# Bare Except Clause



\## Rule

`except:` with no specified exception type catches \*all\* exceptions, including ones you didn't anticipate (like `KeyboardInterrupt` or genuine bugs), silently hiding them.



\## Why it matters

A bare except can mask real bugs, making them very hard to debug later since the program just silently continues instead of failing visibly. It's considered a significant anti-pattern in professional Python code.



\## What good looks like

```python

try:

&#x20;   value = 1 / x

except ZeroDivisionError:

&#x20;   value = 0

```



\## Common student mistake

Using a bare `except: pass` to "make an error go away" during debugging and forgetting to fix it properly afterward.



\## Feedback tone guidance for LLM

Explain the risk concretely (what kind of bug this could hide) rather than just citing the rule.

