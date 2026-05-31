# CR — feature

## Design

新增 sessions 路由，实现 POST /api/sessions（创建 session_id）和 GET /api/sessions/{session_id}（返回初始状态）。

## Source Details

- `routers/sessions.py`: `POST ""` 生成 UUID 返回；`GET "/{session_id}"` 返回固定初始状态（stage="idle"），后续步骤中会改为从 checkpointer 推导真实 stage
- `main.py`: 新增 `app.include_router(sessions.router)`

## Source Tree

```
hire-panel/backend/
├── main.py                  ← added include_router
├── routers/
│   ├── __init__.py          ← new
│   └── sessions.py          ← new
└── schemas/
    ├── __init__.py          ← new
    └── session.py           ← new
```

## Test Details

启动服务：
```
uv run --env-file .env uvicorn backend.main:app --reload
```

验证 1 — 创建 session：
```
curl -X POST http://localhost:8000/api/sessions
```
预期：`{"session_id": "<uuid>"}`

验证 2 — 查询 session 状态（用上一步返回的 uuid）：
```
curl http://localhost:8000/api/sessions/<session_id>
```
预期：`{"session_id":"...","stage":"idle","criteria":[],"resumes":[],"hr_memory":{...}}`

## Test Tree

```
(无变更)
```
