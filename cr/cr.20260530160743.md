# CR — feature

## Design

创建 FastAPI app 入口，lifespan 负责 DB 连接的启动与关闭。

## Source Details

- `backend/main.py`: `lifespan` 在 startup 调 `init_db()`、shutdown 调 `close_db()`；Windows 下在模块加载时设置 `WindowsSelectorEventLoopPolicy`（psycopg3 不兼容 ProactorEventLoop）

## Source Tree

```
hire-panel/backend/
├── __init__.py          ← new (package marker)
├── main.py              ← new
└── services/
    └── __init__.py      ← new (package marker)
```

## Test Details

手动验证步骤：

1. 确认 `.env` 中的 `NEON_DATABASE_URL` 不含 `channel_binding=require`（测试步骤 1 时发现该参数在 Windows 上不兼容 psycopg3）
2. 运行：
   ```
   uv run --env-file .env uvicorn backend.main:app --reload
   ```
3. 预期输出中出现：
   ```
   Application startup complete.
   ```
   且无报错，即验证通过。

## Test Tree

```
(无变更)
```
