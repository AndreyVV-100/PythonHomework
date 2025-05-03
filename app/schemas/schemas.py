from datetime import date, timedelta
from pydantic import (BaseModel, Field, BeforeValidator, EmailStr)
from pydantic_settings import SettingsConfigDict
from typing import Optional, Annotated, TypeAlias
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field as SQLField

class TaskCreate(BaseModel):
    description: str = Field(
        description="Описание задачи",
        max_length=300
    )

    deadline: Optional[date] = Field(
        description="Крайний срок исполнения задачи. "
                    "Не допускаются даты, более ранние, "
                    "чем сегодняшняя.",
        gt=date.today() - timedelta(days=1),
        default_factory=lambda: date.today() + timedelta(days=1)
    )

    priority: Optional[int] = Field(
        description = "Приоритет задачи от 1 (низкий) до 5 (самый высокий).",
        gt = 0,
        lt = 6,
        default_factory = lambda: 3
    )

    estimated_time: Optional[float] = Field(
        description = "Требуемое на задачу время (в часах).",
        gt = 0,
        default_factory = lambda: 1.0
    )

    needed_role: str = Field(
        description = "Квалификация для выполнения задачи"
    )


class TaskRead(TaskCreate):
    task_id: int
    deadline: date
    priority: int
    estimated_time: float

class Task(SQLModel, TaskRead, table=True):
    task_id: int = SQLField(default=None, nullable=False, primary_key=True)
    # project: int = SQLField(default=None, nullable=True, foreign_key="project.project_id")
