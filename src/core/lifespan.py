import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.auction.watcher import auction_watcher
from src.database import engine
from src.core.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(auction_watcher())
    yield
