"""Initialize FastAPI and database"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import (assignment, auth, task, utils)
from app.db import init_database

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize database"""
    init_database()
    yield

app = FastAPI(
    title="Система управления задачами",
    description="Простейшая система управления задачами, основанная на "
                "фреймворке FastAPI.",
    version="0.0.1",
    contact={
        "name": "Андрей Вязовцев",
        "url": "https://github.com/AndreyVV-100"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    # Uncomment if you need to create tables on app start
    lifespan=lifespan
)

app.include_router(assignment.router)
app.include_router(auth.router)
app.include_router(task.router)
app.include_router(utils.router)
