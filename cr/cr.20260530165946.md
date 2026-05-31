# CR — feature

## Design

新增 graph_runner 服务，封装三个 graph 的构建，注入 PG checkpointer。

## Source Details

- `backend/services/graph_runner.py`: `get_jd_graph()` / `get_resume_graph()` / `get_feedback_graph()` 各自调用 `build_*_graph(get_checkpointer())`

## Source Tree

```
hire-panel/backend/services/
├── db.py              (existing)
└── graph_runner.py    ← new
```

## Test Details

临时脚手架 `test_graph_runner.py`（Task B2 完成后删除）：连接 DB 后调用三个 getter，验证返回 `CompiledStateGraph` 且节点列表正确。

```
uv run --env-file .env python test_graph_runner.py
```

## Test Tree

```
hire-panel/
└── test_graph_runner.py    ← 临时脚手架，Task B2 后删除
```

## Test Result

脚手架执行通过：

```
OK: jd_graph       — CompiledStateGraph, nodes=['__start__', 'extract_jd', 'approve_criteria']
OK: resume_graph   — CompiledStateGraph, nodes=['__start__', 'score_resumes']
OK: feedback_graph — CompiledStateGraph, nodes=['__start__', 'process_feedback', 'rescore_all']
--- Task B1 verified ---
```
