#!/usr/bin/env python3
"""
Starts uvicorn with SelectorEventLoop to satisfy psycopg3 on Windows.
Newer uvicorn passes its own loop_factory to asyncio_run(), bypassing
set_event_loop_policy(). Using asyncio.run(loop_factory=...) is the
authoritative fix recommended by psycopg3's own error message.
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn


async def _serve() -> None:
    config = uvicorn.Config("backend.main:app", host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    if sys.platform == "win32":
        import selectors
        asyncio.run(
            _serve(),
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
        )
    else:
        asyncio.run(_serve())
