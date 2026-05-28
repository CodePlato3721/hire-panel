# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workflow Rules

- **Never commit changes directly.** After making any code modifications, stop and wait for the user to review the diff before creating any git commit.

## Commands

```bash
# Install dependencies
uv sync

# Run the full pipeline (requires OPENAI_API_KEY and manual HR approval input)
python main.py

# Run the Streamlit UI
uv run streamlit run app.py

# Run individual integration test flows
python tests/integration/test_jd_flow.py
python tests/integration/test_resume_flow.py
python tests/integration/test_feedback_flow.py
```

The project has no lint or unit test configuration yet. Integration tests are standalone scripts, not pytest suites.

## Environment

Set `OPENAI_API_KEY` before running anything — all nodes call GPT-4o-mini.

## Current Status

- JD flow (Graph 1) and resume scoring flow (Graph 2) integration tests pass.
- Feedback flow (Graph 3) has a known bug: `FeedbackAnalysis.updated_criteria` is typed as `list[dict]`, which OpenAI structured output rejects. **Fix**: replace with `list[UpdatedCriterion]` (a Pydantic `BaseModel` with `name: str` and `description: str`), then convert back to dicts in `process_feedback.py` before writing to state.
- Streamlit UI not yet started.

## Architecture

Three independent LangGraph state machines run sequentially to automate resume screening:

1. **JD Graph** (`pipeline/jd_graph.py`): Extracts 4–6 scoring criteria from raw job description text. Includes a human-in-the-loop interrupt at `approve_criteria` — execution pauses for HR to approve or revise the criteria before continuing.

2. **Resume Graph** (`pipeline/resume_graph.py`): Scores each resume against approved criteria. Scoring is sequential (not parallel) and incorporates `HRMemory` (scoring preferences + adjustment history) to calibrate results.

3. **Feedback Graph** (`pipeline/feedback_graph.py`): Processes HR feedback after initial scoring. Extracts general preferences (reusable rules) and specific adjustments (one-time changes), updates `HRMemory`, then re-scores all resumes from scratch.

`main.py` orchestrates all three flows in order.

### Key files

| Path | Role |
|---|---|
| `pipeline/state.py` | All shared TypedDict state schemas: `JDState`, `ResumeState`, `HRMemory`, `Resume`, `ScoringCriteria` |
| `pipeline/schemas/` | Pydantic models used for structured LLM output (`.with_structured_output()`) |
| `pipeline/nodes/` | One file per graph node — each is a plain function that takes and returns state |
| `pipeline/prompts/` | System prompts for each node, kept separate from node logic |
| `tests/integration/sample_data.py` | `SAMPLE_JD` and `SAMPLE_RESUME` constants used across test flows |

## Next Steps

1. Fix `FeedbackAnalysis` schema bug → verify all 3 integration tests pass end-to-end
2. Build Streamlit UI (left panel: JD criteria + resume table; right panel: chat window with "Fill JD" / "Upload Resumes" quick-action buttons)
3. Add PDF parsing via `pdfplumber` as a preprocessing step before scoring

## Architecture

### Score design

Each criterion is scored 1–10; `total_score` is the raw sum — not normalized to 100. HR uses scores for relative ranking only.

### Design conventions

- All LLM calls use `ChatOpenAI(model="gpt-4o-mini", temperature=0)` with `.with_structured_output()` — never free-form text parsing.
- Human interrupts use `langgraph.types.interrupt()` inside a node; callers resume by invoking the graph with `Command(resume=<feedback>)`.
- Graph state is persisted with `MemorySaver` and scoped by `thread_id` in `configurable` — each test flow uses its own thread.
- `HRMemory` accumulates across feedback rounds; pass it forward explicitly when chaining the resume and feedback graphs. Currently in-memory only; plan is to persist to a markdown file in a future iteration.
