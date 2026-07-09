\# Subject 9 — Automated Student Code Evaluation



Summer internship project (ESPRIT, 4th year, Software Engineering) — academic supervisor: Sirine Naifar.



Goal: an intelligent pipeline that gives students automated, pedagogically-grounded feedback on their code, combining static analysis, RAG, and LLM generation.



\## Status: Week 1



This week focuses on the first two architecture layers (\*\*Couche 1 — Ingestion\*\* and \*\*Couche 2 — Analyse statique\*\*), plus a minimal API layer (\*\*Couche 5\*\*).



\### What's built

\- A Python static code analyzer built with the built-in `ast` module (no third-party analysis libraries), detecting:

&#x20; - Missing docstrings

&#x20; - Functions with too many parameters

&#x20; - High cyclomatic complexity

&#x20; - Overly long functions

&#x20; - Naming convention violations (snake\_case for functions, PascalCase for classes)

\- A FastAPI endpoint (`POST /analyze`) that accepts a `.py` file and returns a structured JSON report

\- Swagger UI auto-documentation at `/docs`



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



\## Next steps (Week 2+)

\- Extend static analysis (SonarQube integration)

\- Build the pedagogical knowledge base (rubrics, guidelines) — Couche 3

\- Vectorize and index with ChromaDB / sentence-transformers

\- RAG-grounded LLM feedback generation — Couche 4

