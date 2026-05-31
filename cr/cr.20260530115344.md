# CR — feature

## Design

新增 AsyncPostgresSaver 连接服务，用于将 LangGraph checkpointer 接入 neon.tech PostgreSQL。

## Source Details

- `pyproject.toml`: 新增 `fastapi`, `uvicorn[standard]`, `psycopg[binary,pool]`, `langgraph-checkpoint-postgres` 四个依赖
- `backend/services/db.py`: `init_db()` 创建 `AsyncConnectionPool` 并调用 `checkpointer.setup()` 建表；`get_checkpointer()` 供其他模块取用；`close_db()` 释放连接池

## Source Tree

```
hire-panel/
├── pyproject.toml                  ← added backend dependencies
└── backend/
    └── services/
        └── db.py                   ← new
```

## Test Details

无。

## Test Tree

```
(无变更)
```
