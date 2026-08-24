# Subject 9 — Code Evaluation Web Interface

A React + TypeScript frontend for the Subject 9 automated code evaluation API
(FastAPI + static analysis + RAG + LLM feedback + sandboxed exam grading).

## Stack
- React 19 + TypeScript
- Vite (build tool)
- Tailwind CSS v4

## Setup

```bash
npm install
cp .env.example .env
# edit .env if your backend isn't on http://localhost:8000
npm run dev
```

Open http://localhost:5173. The backend (FastAPI) must be running separately —
see the main project README for how to start it, and make sure CORS is enabled
there (see backend/main.py).

## Build for production

```bash
npm run build
```

Outputs static files to `dist/`, deployable to any static host (Vercel, Netlify,
GitHub Pages).

## Project structure

```
src/
  types/api.ts          TypeScript types mirroring the backend's response shapes
  lib/api.ts             Typed fetch client for /analyze and /evaluate-exam
  components/
    shared/               Header, TabBar, empty/loading/error states
    analyze/              Code Review tab: form + issue cards
    exam/                 Exam Grading tab: form, grade stamp, test table
  App.tsx                 Top-level state and layout
```
