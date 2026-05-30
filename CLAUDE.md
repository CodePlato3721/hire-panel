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

## CR(commit request)

每次模型修改完代码**必须**不直接 commit，并且生成一份 CR(commit request)。
CR 的作用是修改的摘要，方便用户以及其他 agent 了解改动。
CR 生成后会回显给用户，并且写入 `.cr.md` 文件。

### CR 的 reply

CR 创建后等待用户 reply。reply 分为 3 种：
- **approve**：执行 commit & push 的行为。并进行**reply 后的 CR 文件操作**
- **reject**：回滚所有改动。并进行**reply 后的 CR 文件操作**
- **modify**：modify 不是一种 reply。用户可以不说 modify。用户只需要 1. 自己手动更改，并要求模型再次生成 CR。 2. 让模型修改代码，模型自动再生成一次 CR。 3. 用户只是询问修改的细节，但是不做任何修改，也不再次生成 CR。再次生成 CR 后继续等待用户的 reply，重复这个动作

### reply 后的 CR 文件操作

CR 文件**只存储在本地**，不会提交。如果用户 reply 是 approve 或者 reject，则在执行相对应的操作后，对 CR 进行如下操作：
- `.cr.md` 被重命名为 `.cr.<timestamp>.md`，`timestamp` 格式 `yyyyMMddhhmmss`
- 重命名后被移入 `.cr` 文件夹。如果没有 `.cr` 文件夹就新建
- `.cr.md` 和 `.cr` 文件夹都会被加入 `.gitignore`

### CR 的格式

CR 根据改动分为 2 种：feature 和 defect。以下是两种 CR 的格式。

#### feature

包含以下结构：
- **Design**：本次改动的设计摘要
- **Source Details**：本次改动的源码的核心细节摘要。非核心改动不需要提及。核心改动只需要提 1~2 行代码，简短。不包含测试用例的改动
- **Source Tree**：本次改动的源代码文件树
- **Test Details**：本次改动的测试用例的改动摘要
- **Test Tree**：本次改动的测试用例文件树

#### defect

包含以下结构：
- **Root Cause**：这个 defect 的 Root Cause
- **Solution**：修改方案的摘要
- **Source Details**：本次改动的源码的核心细节摘要。非核心改动不需要提及。核心改动只需要提 1~2 行代码，简短。不包含测试用例的改动
- **Source Tree**：本次改动的源代码文件树
- **Test Details**：本次改动的测试用例的改动摘要
- **Test Tree**：本次改动的测试用例文件树