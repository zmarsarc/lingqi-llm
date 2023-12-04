from fastapi import FastAPI
from .router import router_v1
from .api.admin import router as admin_api

app = FastAPI()
app.include_router(router_v1, prefix='/app')

admin = FastAPI()
admin.include_router(admin_api, prefix='/admin')
