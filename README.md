# Automated Student Code Evaluation

Summer internship project (ESPRIT, 4th year, Software Engineering) — academic supervisor: Sirine Naifar.

An intelligent evaluation system combining static analysis, RAG (Retrieval-Augmented Generation), and LLM-based feedback generation, operating in two modes:

1. **Generic code quality evaluation** — analyzes any Python submission for code quality issues and generates grounded, pedagogical feedback.
2. **Exam-correction mode** — given an instructor's exam statement (French or English) and a student's submission, automatically extracts constraints and test cases, checks compliance, executes the code safely, and produces a holistic evaluation with a numeric grade out of 20.

## Architecture

Five layers, per the original specifications, plus an exam-correction extension:

| Layer | Component | Technology |
|---|---|---|
| 1 — Ingestion | Single file or zip project upload, safely extracted | FastAPI, custom zip-slip/zip-bomb protection |
| 2 — Static Analysis | Custom rule-based analyzer + industry metrics | Python `ast`, SonarQube (Docker) |
| 3 — RAG Engine | Pedagogical knowledge base, embedded and retrievable | sentence-transformers, ChromaDB |
| 4 — LLM Generation | Grounded feedback generation | Groq API (`openai/gpt-oss-120b`) |
| 5 — Delivery | REST API | FastAPI, Swagger |
| Exam mode | Constraint extraction, multi-language checking, sandboxed execution, holistic grading | Groq, `javalang`, Docker |

See `docs/` (or Chapters 1–2 of the internship report) for full architectural detail and design rationale.

## Features

**Generic evaluation (`POST /analyze`)**
- 10 static analysis rules: missing docstrings, excessive parameters, high cyclomatic complexity, overly long functions, naming violations, unused imports, bare except, magic numbers, unused variables, duplicate functions
- SonarQube integration (Quality Gate passing: 0 bugs, 0 vulnerabilities)
- Accepts a single `.py` file **or a zipped multi-file project**
- Grounded LLM feedback for every issue, batched per file

**Exam-correction mode (`POST /evaluate-exam`)**
- Automatic extraction of banned functions/imports and example test cases from free-text exam instructions — French and English
- Multi-language constraint checking: Python (`ast`) and Java (`javalang`), including qualified method names (e.g. `Arrays.sort`)
- Sandboxed code execution: isolated, network-disabled, resource- and time-limited Docker containers (network isolation proven by an automated test)
- Supports both single-file and multi-file (zip) submissions, with automatic or explicit entry-point resolution
- Holistic evaluation combining constraint violations and real execution results — correctly penalizes "gaming the tests" via banned shortcuts, verified in both Python and Java
- Numeric grading out of 20 (French academic convention)

## Project structure
code-eval/
├── backend/ # FastAPI app (main.py)
├── static_analysis/ # ast analyzer, project-wide aggregation
├── rag/ # embeddings ingestion & retrieval
├── llm/ # generic feedback generation
├── exam_mode/ # constraint extraction/checking, sandbox executors, evaluation
├── project_utils/ # safe zip extraction
├── knowledge_base/ # rubrics.json — the pedagogical knowledge base
├── samples/ # example files for testing
├── tests/ # pytest suite (fast / docker / llm marked)
├── requirements.txt
├── Dockerfile
└── run_dev_server.py # dev server launcher (correct reload-dir scoping)


## Running locally

```bash
pip install -r requirements.txt
python run_dev_server.py
```

Then open `http://127.0.0.1:8000/docs` for the interactive API.

**Requirements**: Docker Desktop must be running for SonarQube and sandboxed execution features.

### Environment variables

Create a `.env` file:
GROQ_API_KEY=your_key_here

## Testing

The suite is organized into three tiers:

```bash
pytest -m "not docker and not llm"   # fast, no external dependencies (~35 tests)
pytest -m docker                      # requires Docker Desktop running
pytest -m llm                         # requires a valid GROQ_API_KEY
pytest                                 # everything
```

## Example usage

**Generic analysis:**
```bash
curl -X POST 'http://127.0.0.1:8000/analyze' \
  -F 'file=@samples/sample_student_code.py'
```

**Exam correction:**
```bash
curl -X POST 'http://127.0.0.1:8000/evaluate-exam' \
  -F 'code_file=@samples/lazy_bubble_sort.py' \
  -F 'instructions_file=@samples/exam_instructions.txt' \
  -F 'language=python'
```

## Key technical decisions

- **JSON knowledge base** (not markdown) — chosen after markdown/YAML frontmatter parsing proved unreliable due to development-environment text encoding issues; a deliberate reliability trade-off.
- **Rule-based (metadata) retrieval** for generic feedback, not semantic search — the analyzer always knows the exact rule that fired, so exact matching is faster and unambiguous. Semantic search is used where it's actually needed: parsing free-text exam instructions with no fixed vocabulary.
- **Groq API** (`openai/gpt-oss-120b`) instead of Claude/GPT-4o — no funded API account was available for this internship; mitigated by prior experience with the same provider and defensive JSON parsing throughout. (Originally `llama-3.3-70b-versatile`, migrated after upstream deprecation.)
- **Docker-based sandboxing** for exam-mode code execution — network-disabled, resource-capped, timeout-protected; verified by automated tests, not just asserted.

## Known limitations / future work

- Exam-mode sandboxed execution currently supports Python and Java only.
- Cloud deployment with full functionality requires Docker-in-Docker support, which most standard free hosting platforms do not provide by default; current deployment is local / tunnel-based.
- Evaluation on a larger corpus of real student submissions is ongoing.

## Author

Amani Ghribi — ESPRIT, Software Engineering, 4th year