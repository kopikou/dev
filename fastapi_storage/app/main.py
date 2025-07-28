from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_storage.app.database import async_db, Base
from fastapi_storage.app.routers import router
from fastapi_storage.app.models import FileTypeEnum, FileType
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
async def create_tables():
    async with async_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def init_file_types():
    async for session in async_db.get_async_session():
        try:
            for filetype in FileTypeEnum:
                existing_type = await session.get(FileType, filetype.value)
                if not existing_type:
                    session.add(FileType(id=filetype.value, name=filetype.name))
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise

@app.on_event("startup")
async def on_startup():
    await create_tables()
    await init_file_types() 
app.include_router(router)


