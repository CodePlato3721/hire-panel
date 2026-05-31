# CR — feature

## Design

将三个 pipeline graph 的 checkpointer 从硬编码 InMemorySaver 改为外部参数注入。

## Source Details

- `pipeline/jd_graph.py`, `resume_graph.py`, `feedback_graph.py`: 移除 `InMemorySaver` import，`build_*_graph()` 签名改为 `build_*_graph(checkpointer)`

## Source Tree

```
hire-panel/
├── pipeline/
│   ├── jd_graph.py        ← checkpointer parameter
│   ├── resume_graph.py    ← checkpointer parameter
│   └── feedback_graph.py  ← checkpointer parameter
└── TASKS.md               ← Task A marked done
```

## Test Details

integration tests 已同步更新，传入 `InMemorySaver()` 保持原有行为：

```
uv run python tests/integration/test_jd_flow.py
uv run python tests/integration/test_resume_flow.py
uv run python tests/integration/test_feedback_flow.py
```

三个脚本均应正常运行（需要 `OPENAI_API_KEY`）。

## Test Tree

```
tests/integration/
├── test_jd_flow.py       ← pass InMemorySaver()
├── test_resume_flow.py   ← pass InMemorySaver()
└── test_feedback_flow.py ← pass InMemorySaver()
```
