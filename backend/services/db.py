import os
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

_pool: AsyncConnectionPool | None = None
_checkpointer: AsyncPostgresSaver | None = None


async def init_db() -> None:
    global _pool, _checkpointer
    url = os.environ["NEON_DATABASE_URL"]
    _pool = AsyncConnectionPool(conninfo=url, min_size=0, max_size=10, max_idle=60, open=False)
    await _pool.open()
    _checkpointer = AsyncPostgresSaver(_pool)
    await _checkpointer.setup()


async def close_db() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("DB not initialized — call init_db() first")
    return _checkpointer
