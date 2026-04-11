from fastapi import APIRouter

from .models import router as models_router
from .chat import router as chat_router
from .token import router as token_router


router = APIRouter()
router.include_router(models_router)
router.include_router(chat_router)
router.include_router(token_router)
