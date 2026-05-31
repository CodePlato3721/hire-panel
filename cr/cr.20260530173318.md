# CR — feature

## Design

新增 JD 端点：POST /jd 提交 JD 并启动 graph，POST /jd/reply 恢复审批，均以 SSE 流返回；astream_events 调用留在各端点，events 结果传给 _stream_jd 处理，事件解析由公共函数 events_to_sse_tokens 负责。

## Source Details

- `backend/routers/sse.py`: `events_to_sse_tokens(events)` 从 `astream_events` 输出中提取 `on_chat_model_stream` 事件，yield SSE token 字符串
- `backend/routers/jd.py`: 各端点调用 `graph.astream_events(...)` 拿到 `events`，传给 `_stream_jd(events, graph, config)`；`_stream_jd` 负责 token 流 + `aget_state` + JD 特有的 `done` 事件
- `backend/main.py`: 新增 `app.include_router(jd.router)`

## Source Tree

```
hire-panel/backend/
├── main.py                ← added include_router(jd.router)
├── routers/
│   ├── jd.py              ← new
│   └── sse.py             ← new (common SSE parser)
└── schemas/
    └── jd.py              ← new
```

## Test Details

人工测试步骤（需要 `OPENAI_API_KEY` 和 neon.tech 连接）：

**1. 启动服务**
```
uv run --env-file .env uvicorn backend.main:app --reload
```

**2. 创建 session**
```
curl -s -X POST http://localhost:8000/api/sessions
# 记录返回的 session_id，例如 "abc-123"
```

**3. 提交 JD（预期：token 流 + done 事件 interrupted=true）**
```
curl -N -X POST http://localhost:8000/api/sessions/abc-123/jd \
  -H "Content-Type: application/json" \
  -d "{\"jd_text\": \"We are looking for a Python engineer with 5 years experience.\"}"
```

**4. 审批（预期：token 流 + done 事件 interrupted=false，criteria 非空）**
```
curl -N -X POST http://localhost:8000/api/sessions/abc-123/jd/reply \
  -H "Content-Type: application/json" \
  -d "{\"reply\": \"ok\"}"
```

验证重点：两次请求使用同一 session_id，第二次能从 PostgreSQL checkpointer 恢复第一次的中断状态。

## Test Tree

```
(无变更)
```

## Test Result

人工测试，不提供 Test Result，具体验证方式见 Test Details。
