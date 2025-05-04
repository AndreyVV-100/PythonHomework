from fastapi import FastAPI
from app.routes import (auth, task, utils)

# Uncomment if you need to create tables on app start >>>
from contextlib import asynccontextmanager
from app.db import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(auth.router)
app.include_router(task.router)
app.include_router(utils.router)
