from fastapi import FastAPI

from src.config import get_settings
from src.core.lifespan import lifespan
from src.lots.router import router as lots_router
from src.router import root_router
from src.websocket.router import ws_router

settings = get_settings()


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

app.include_router(ws_router)

app.include_router(root_router)
app.include_router(lots_router, prefix="/lots", tags=["Lots"])

