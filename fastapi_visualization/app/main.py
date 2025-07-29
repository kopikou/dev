from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_visualization.app.routers import router

app = FastAPI()

app.include_router(router)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
