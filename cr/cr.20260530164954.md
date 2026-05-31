# CR — feature

## Design

将三个 pipeline graph 的 checkpointer 从硬编码 InMemorySaver 改为外部参数注入。

## Source Details

- `pipeline/jd_graph.py`, `resume_graph.py`, `feedback_graph.py`: 移除 `InMemorySaver` import，`build_*_graph()` 签名改为 `build_*_graph(checkpointer)`，compile 时使用传入的 checkpointer

## Source Tree

```
hire-panel/pipeline/
├── jd_graph.py        ← build_jd_graph(checkpointer)
├── resume_graph.py    ← build_resume_graph(checkpointer)
└── feedback_graph.py  ← build_feedback_graph(checkpointer)
```

## Test Details

三个 integration test 同步更新，各自传入 `InMemorySaver()` 保持原有行为：

```
uv run --env-file .env python main.py
```

## Test Tree

```
hire-panel/tests/integration/
├── test_jd_flow.py       ← pass InMemorySaver()
├── test_resume_flow.py   ← pass InMemorySaver()
└── test_feedback_flow.py ← pass InMemorySaver()
```

## Test Result

集成测试全部通过（`uv run --env-file .env python main.py`）：

- **STEP 1 JD flow**：成功提取 5 条 criteria，HR approve 后继续
- **STEP 2 Resume flow**：john_doe.pdf 评分 49 pts
- **STEP 3 Feedback flow**：反馈处理完成，重新评分 49 pts

3 个 flow 均无异常。
