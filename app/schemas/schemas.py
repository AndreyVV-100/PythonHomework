"""SQL models for database and routes"""

from datetime import date, timedelta
from typing import Optional
from pydantic import (BaseModel, Field)
from pydantic_settings import SettingsConfigDict
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field as SQLField

class TaskCreate(BaseModel):
    """Model for task creation"""
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
        description = "Квалификация для выполнения задачи."
    )

class TaskRead(TaskCreate):
    """Model for task reading"""
    task_id: int
    deadline: date
    priority: int
    estimated_time: float

class Task(SQLModel, TaskRead, table=True):
    """Model for tasks database"""
    task_id: int = SQLField(default=None, nullable=False, primary_key=True)

class User(SQLModel, table=True):
    """Model for users database"""
    __table_args__ = (UniqueConstraint("email"),)
    user_id: int = SQLField(default=None, nullable=False, primary_key=True)
    email: str = SQLField(nullable=True, unique_items=True)
    password: str
    first_name: str
    last_name: str
    role: str
    workload: float

    model_config = SettingsConfigDict(
        json_schema_extra = {
            "example": {
                "first_name": "Иван",
                "last_name": "Иванов",
                "role": "senior",
                "email": "user@example.com",
                "password": "qwerty",
                "workload": 0.0
            }
        })

class Assignment(SQLModel, table=True):
    """Model for assignments database"""
    assignment_id: int = SQLField(default=None, nullable=False, primary_key=True)
    task_id: int = SQLField(nullable=False, unique_items=True)
    user_id: int
