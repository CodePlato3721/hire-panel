# Hire Panel

An AI-powered resume screening tool. Paste a job description, let the AI extract scoring criteria, upload resumes to score them, then refine results with natural-language feedback.

## Features

- **Criteria extraction** — paste a job description; the AI extracts 4–6 structured scoring criteria with a human-in-the-loop approval step
- **Resume scoring** — upload PDF resumes; each is scored against the criteria and displayed as `score / max` with a summary
- **Feedback loop** — give natural-language feedback (e.g. "weight cloud experience more heavily") and the AI re-scores all resumes, remembering your preferences across rounds
- **Split-panel UI** — criteria and resume scores on the left, conversational interface on the right

## Tech Stack

| Layer | Library |
|---|---|
| Frontend | React + TypeScript (Vite) |
| Backend | FastAPI + Server-Sent Events |
| LLM orchestration | LangGraph |
| LLM provider | OpenAI GPT-4o-mini |
| Checkpoint storage | Neon PostgreSQL (`psycopg_pool`) |
| Data validation | Pydantic |

## Getting Started

**Prerequisites:** Python 3.12+, [uv](https://github.com/astral-sh/uv), Node.js 18+, an OpenAI API key, a Neon database URL.

### Backend

```bash
# Install dependencies
uv sync

# Create .env in the project root
OPENAI_API_KEY=sk-...
NEON_DATABASE_URL=postgresql://...

# Start the backend (port 8000)
uv run --env-file .env python scripts/run_server.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

## Usage

1. Click **Fill JD** in the right panel and paste the job description
2. Review the extracted criteria; reply with `approve` or send revisions
3. Click **Upload Resumes** and select PDF files
4. Scores appear in the left panel as `score / max` with a one-line summary per resume
5. Enter feedback in the right panel to re-score; the AI updates scores and remembers your preferences

## Project Structure

```
hire-panel/
├── backend/
│   ├── main.py                 # FastAPI app + lifespan (DB init/close)
│   ├── routers/                # HTTP + SSE route handlers
│   ├── services/               # Business logic (session, JD, resume, feedback)
│   │   └── db.py               # Postgres connection pool + checkpointer
│   └── pipeline/               # LangGraph pipelines
│       ├── jd_graph.py         # JD → criteria extraction (with HR approval interrupt)
│       ├── resume_graph.py     # Resume scoring
│       ├── feedback_graph.py   # Feedback processing + re-scoring
│       ├── nodes/              # Individual graph node implementations
│       ├── prompts/            # LLM prompt templates
│       └── schemas/            # Pydantic structured-output schemas
├── frontend/
│   └── src/
│       ├── App.tsx             # Root layout (split panel)
│       ├── api.ts              # Typed API + SSE client
│       ├── components/         # CriteriaList, ResumeTable, JdFlow, ResumeUpload, FeedbackChat
│       └── hooks/              # useSession, useJdFlow, useResumeUpload, useFeedback
├── tests/
│   └── e2e/                    # Integration test scripts
├── scripts/
│   └── run_server.py           # Dev server launcher
└── pyproject.toml
```
