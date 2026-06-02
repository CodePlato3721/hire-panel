# CR — feedback 业务逻辑下沉到 services 层

**Type**: feature

---

## Design

将 `feedback.py` router 中的全部业务逻辑提取到 `backend/services/feedback.py`，router 只保留 HTTP 入参/出参；`_get_prev_feedback` 封装"从 feedback 或 resume 图读取上一轮状态"的逻辑，`build_feedback_stream` 组装图事件流。

---

## Source Details

```python
# services/feedback.py
async def build_feedback_stream(session_id: str, feedback_text: str):
    ...
    resumes, hr_memory = await _get_prev_feedback(session_id, checkpointer, graph, feedback_config)
    events = graph.astream_events({...}, feedback_config, version="v2")
    return events, graph, feedback_config

# routers/feedback.py — router 只剩 3 行核心逻辑
async def submit_feedback(session_id: str, req: FeedbackRequest):
    events, graph, config = await build_feedback_stream(session_id, req.feedback)
    return StreamingResponse(_stream_feedback(events, graph, config), ...)
```

---

## Source Tree

```
backend/
├── services/
│   └── feedback.py    ← new: _get_prev_feedback, build_feedback_stream
└── routers/
    └── feedback.py    ← updated: 删除全部业务逻辑，调用 build_feedback_stream
```

---

## Test Details

5 个现有单元测试全部通过，无行为变更。

---

## Test Tree

```
tests/unit/
└── test_get_session.py    ← unchanged: 5 tests
```

---

## Test Result

5 passed / 0 failed（`uv run pytest tests/unit/test_get_session.py -v`，Duration 1.40s）

---

## Reply

approve
