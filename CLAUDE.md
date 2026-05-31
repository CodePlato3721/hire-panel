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

## 单次改动规范

### 颗粒度

每一次改动保持小颗粒度。颗粒度判断标准：

- **同层改动**：单次改动尽量只改同一层。改 service 就不改 router/view；改业务逻辑 py 就不改 REST API 层。
- **一句话概括检验**：本次改动的 CR 中，Design（feature）或 Solution（defect）必须能用一句简短的话概括完。如果需要列多件事才能描述清楚，说明颗粒度太大，应拆分。
- **颗粒度不应过小**：如果本次改动本身就只涉及配置（例如某个 defect 就是配置错误，或本次只改 `CLAUDE.md` / `.gitignore`），则配置单独成一个 CR 是合理的。但如果配置改动是为了支撑业务逻辑改动（例如为新功能新增依赖），则依赖变更与源码改动应合并在同一个 CR 里，不应拆开。
- **改动必须闭合**：每次改动都必须有验证手段，保证不会提交错误代码后再修改。验证方式按优先级：
  1. 项目已有对应层的**单元测试** → 随改动一起更新，CR 的 Test Details 写测试摘要。
  2. 项目已有**端到端测试** → 随改动一起更新，CR 的 Test Details 写测试摘要。
  3. 无自动化测试 → 在 CR 的 Test Details 里写清楚**手动验证步骤**，告诉用户执行哪条命令或操作来验证本次改动正确。
  4. 连手动验证都难以做到（例如改动依赖外部环境尚未就绪）→ 在本次改动中附上**临时测试脚手架代码**，CR 注明"下次改动删除脚手架"，下一个 CR 中去除。

### CR（commit request）

每次模型修改完代码**必须**不直接 commit，并且生成一份 CR。
CR 的作用是改动摘要，方便用户及其他 agent 了解改动。
CR 生成后回显给用户，并写入 `.cr.md` 文件。

**CR 回显规则**：回显给用户的 Chat 版本必须与 `.cr.md` 完全一致，包含所有字段，不得省略任何一项。缺少任何字段的 CR 视为不合规。

#### CR 的 reply

CR 创建后等待用户 reply。reply 分为 3 种：
- **approve**：执行 commit & push。并进行**reply 后的 CR 文件操作**。
- **reject**：回滚所有改动。并进行**reply 后的 CR 文件操作**。
- **modify**：modify 不是一种 reply。用户可以不说 modify。用户只需要：1. 自己手动更改并要求模型再次生成 CR；2. 让模型修改代码，模型自动再生成一次 CR；3. 用户只是询问细节，不做修改也不再次生成 CR。再次生成 CR 后继续等待 reply，重复此动作。

#### reply 后的 CR 文件操作

CR 文件**只存储在本地**，不会提交。approve 或 reject 执行完对应操作后：
- `.cr.md` 重命名为 `.cr.<timestamp>.md`，`timestamp` 格式 `yyyyMMddhhmmss`
- 移入 `.cr` 文件夹（不存在则新建）
- `.cr.md` 和 `.cr/` 已加入 `.gitignore`

#### CR 的格式

CR 分为 feature 和 defect 两种。

**Source Tree** 和 **Test Tree** 必须使用 ASCII 文件树格式，不可以用一句话代替，例如：
```
project/
├── src/
│   └── service.py    ← updated
└── tests/
    └── test_service.py    ← new
```

**feature**
- **Design**：本次改动的设计摘要
- **Source Details**：源码核心细节，1~2 行代码，简短，不含测试改动
- **Source Tree**：本次改动的源码文件树（ASCII 树）
- **Test Details**：测试改动摘要；若无自动化测试，写手动验证步骤；若附有脚手架代码，注明下次删除
- **Test Tree**：本次改动的测试文件树（ASCII 树）；若无测试文件改动，写 `(无变更)` 占位
- **Test Result**：见下方说明

**defect**
- **Root Cause**：defect 的根本原因
- **Solution**：修改方案摘要
- **Source Details**：源码核心细节，1~2 行代码，简短，不含测试改动
- **Source Tree**：本次改动的源码文件树（ASCII 树）
- **Test Details**：测试改动摘要；若无自动化测试，写手动验证步骤；若附有脚手架代码，注明下次删除
- **Test Tree**：本次改动的测试文件树（ASCII 树）；若无测试文件改动，写 `(无变更)` 占位
- **Test Result**：见下方说明

**Test Result 规则**
根据本次改动的测试文件类型，分为三种情况：
- **单元测试**：模型自己执行单元测试，将执行结果摘要写入 Test Result（通过/失败条数、失败原因）
- **集成测试**：模型自己执行集成测试，将执行结果摘要写入 Test Result
- **人工测试**：写 `人工测试，不提供 Test Result，具体验证方式见 Test Details`