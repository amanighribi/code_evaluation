\---

rule\_id: function\_too\_long

category: maintainability

severity: minor

source: "Clean Code (Robert C. Martin) — functions should be small"

analyzer\_check: "length > 30 lines"

\---



\# Function Too Long



\## Rule

A function longer than \~30 lines is often doing more than one job and is a candidate for splitting into smaller, named helper functions.



\## Why it matters

Shorter functions are easier to read in one glance, easier to name meaningfully, and easier to reuse and test independently.



\## What good looks like

Extract logically distinct steps into helper functions with descriptive names, so the main function reads like a short list of steps.



\## Common student mistake

Writing one large function that handles input validation, processing, and output formatting all in one block.



\## Feedback tone guidance for LLM

Suggest specific extraction points if identifiable (e.g. "the validation logic at the start could become its own function").

