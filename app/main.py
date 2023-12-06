from fastapi import FastAPI
from .router import api_router_v1, admin_router

app = FastAPI()
app.include_router(api_router_v1, prefix='/app')

admin = FastAPI()
admin.include_router(admin_router, prefix='/admin')
