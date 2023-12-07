from fastapi import FastAPI
from .router import api_router_v1, admin_router
from contextlib import asynccontextmanager
from app.service.db import close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    # close database connection before shutdown.
    await close_database()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router_v1, prefix='/app')

admin = FastAPI(lifespan=lifespan)
admin.include_router(admin_router, prefix='/admin')
