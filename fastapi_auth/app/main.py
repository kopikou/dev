from fastapi import FastAPI
from fastapi_auth.app.auth.schemas import UserRead, UserUpdate
from fastapi_auth.app.auth.routers import router as auth_router
from fastapi_auth.app.auth.manager import fastapi_users
from fastapi_auth.app.group.routers import router as group_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi_auth.app.auth.models import User  # noqa F401 - так надо
from fastapi_auth.app.group.models import Group  # noqa F401 - так надо


app = FastAPI()

app.include_router(auth_router)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(group_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


from fastapi_auth.app.database import async_db, Base

@app.on_event("startup")
async def startup_db():
    async with async_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)