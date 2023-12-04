from fastapi import APIRouter
from . import api

router_v1 = APIRouter(prefix='/v1')

router_v1.include_router(api.auth_api)
router_v1.include_router(api.user_api)
router_v1.include_router(api.chat_api)