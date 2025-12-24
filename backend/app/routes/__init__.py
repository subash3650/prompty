"""API routes package."""

from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.game import router as game_router
from app.routes.leaderboard import router as leaderboard_router
from app.routes.users import router as users_router
from app.routes.admin import router as admin_router


# Create main API router
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(game_router)
api_router.include_router(leaderboard_router)
api_router.include_router(users_router)
api_router.include_router(admin_router)
