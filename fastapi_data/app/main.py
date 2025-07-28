from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi_data.app.data.routers import router as data_router
from fastapi_data.app.statistic.routers import router as statistic_router
from fastapi_data.app.calculation.routers import router as calculation_router
from fastapi_data.app.memory import RedisConnection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await RedisConnection.connect()
    yield
    await RedisConnection.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(data_router)
app.include_router(statistic_router)
app.include_router(calculation_router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
