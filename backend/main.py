import sys

# psycopg3 requires SelectorEventLoop on Windows (ProactorEventLoop is incompatible)
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.services.db import init_db, close_db
from backend.routers import sessions, jd, resume, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="hire-panel", lifespan=lifespan)
app.include_router(sessions.router)
app.include_router(jd.router)
app.include_router(resume.router)
app.include_router(feedback.router)
