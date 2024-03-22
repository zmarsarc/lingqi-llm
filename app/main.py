from fastapi import FastAPI
from .router import api_router_v1, admin_router
from contextlib import asynccontextmanager
from app.service.db import close_database
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    # close database connection before shutdown.
    await close_database()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router_v1, prefix='/app')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = FastAPI(lifespan=lifespan)
admin.include_router(admin_router, prefix='/admin')
