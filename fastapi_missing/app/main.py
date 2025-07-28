from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi_missing.app.routers import router
from fastapi_missing.app.memory import RedisConnection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await RedisConnection.connect()
    yield
    await RedisConnection.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)