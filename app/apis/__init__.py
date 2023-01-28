from fastapi import APIRouter

from .guilds import router as authRouter
from .messaging import router as messagingRouter
from .dashboard import router as dashboardRouter
from .config import router as configRouter
from .settings import router as settingsRouter

__all__ = [
    "apis",
]
apis = APIRouter()
apis.include_router(authRouter)
apis.include_router(messagingRouter)
apis.include_router(dashboardRouter)
apis.include_router(configRouter)
apis.include_router(settingsRouter)
