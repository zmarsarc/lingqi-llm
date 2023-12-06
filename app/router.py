from fastapi import APIRouter
from . import api
from .api import admin

api_router_v1 = APIRouter(prefix='/v1')

api_router_v1.include_router(api.auth_api)
api_router_v1.include_router(api.user_api)
api_router_v1.include_router(api.chat_api)

admin_router = APIRouter()
admin_router.include_router(admin.router)