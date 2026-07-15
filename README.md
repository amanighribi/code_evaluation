\# Subject 9 — Automated Student Code Evaluation



Summer internship project (ESPRIT, 4th year, Software Engineering) — academic supervisor: Sirine Naifar.



Goal: an intelligent pipeline that gives students automated, pedagogically-grounded feedback on their code, combining static analysis, RAG, and LLM generation.



\## Status: Week 1



This week focuses on the first two architecture layers (\*\*Couche 1 — Ingestion\*\* and \*\*Couche 2 — Analyse statique\*\*), plus a minimal API layer (\*\*Couche 5\*\*).



### What's built
- A Python static code analyzer built with the built-in `ast` module (no third-party analysis libraries), detecting:
  - Missing docstrings
  - Functions with too many parameters
  - High cyclomatic complexity
  - Overly long functions
  - Naming convention violations (snake_case for functions, PascalCase for classes)
  - Unused imports
  - Bare `except:` clauses
  - Magic numbers in comparisons
  - Unused variables
  - Duplicate function bodies
- A FastAPI endpoint (`POST /analyze`) that accepts a `.py` file and returns a structured JSON report
- Swagger UI auto-documentation at `/docs`
- Dockerized (`Dockerfile` + `.dockerignore`) — tested and working via `docker build` / `docker run`
- 11 passing unit tests (`pytest`) covering all detection rules



\### Tech stack (per cahier des charges)

\- Python 3.11+

\- FastAPI

\- `ast` (standard library)



\## Project structure



subject9-code-eval/

├── backend/

│   └── main.py              # FastAPI app

├── static\_analysis/

│   └── analyzer.py          # AST-based static analyzer

├── samples/

│   └── sample\_student\_code.py  # deliberately flawed test file

├── requirements.txt

└── README.md



\## Running locally



```bash

pip install -r requirements.txt

uvicorn backend.main:app --reload

```



Then open `http://127.0.0.1:8000/docs` for the interactive API.



\## Example



```bash

curl -X POST 'http://127.0.0.1:8000/analyze' \\

&#x20; -H 'accept: application/json' \\

&#x20; -F 'file=@samples/sample\_student\_code.py;type=text/x-python'

```



Returns a JSON report with function/class metrics and a list of detected issues.


### Static analysis — dual approach
This project uses two complementary static analysis layers:
- **Custom `ast`-based analyzer** — pedagogically-motivated checks (docstrings, naming, magic numbers, unused imports/variables, duplicate functions) not covered by default SonarQube rules.
- **SonarQube (Community Edition, via Docker)** — industry-standard metrics including Cognitive Complexity, security hotspots, and maintainability rating. Currently passing the default Quality Gate with 0 bugs, 0 vulnerabilities, and 100% coverage on new code.

Run a local SonarQube scan:
```bash
sonar-scanner.bat -D"sonar.login=<your-token>"
```
Results: `http://localhost:9000/dashboard?id=code-eval`

