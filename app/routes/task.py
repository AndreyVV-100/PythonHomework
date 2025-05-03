from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from ..schemas import schemas as schema_task
from typing import Annotated, List

router = APIRouter(prefix="/tasks", tags=["Управление задачами в БД"])


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema_task.TaskRead)
def create_task(task: schema_task.TaskCreate,
                session: Session = Depends(get_session)):
    new_task = schema_task.Task(
        description = task.description,
        deadline = task.deadline,
        priority = task.priority,
        estimated_time = task.estimated_time,
        needed_role = task.needed_role.lower()
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[schema_task.TaskRead])
def read_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(schema_task.Task)).all()
    if tasks is None or len(tasks) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The task list is empty."
        )
    return tasks


@router.get("/{task_id}", response_model=schema_task.TaskRead)
def read_task_by_id(task_id: int,
                    session: Session = Depends(get_session)):
    tasks = session.exec(select(schema_task.Task).where(schema_task.Task.task_id == task_id)).all()
    if tasks is None or len(tasks) != 1:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"No task with {task_id} id."
        )
    return tasks[0]


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=schema_task.TaskRead)
def update_task_by_id(task_id: int, data_for_update: dict,
                      session: Session = Depends(get_session)):
    tasks = session.exec(select(schema_task.Task).where(schema_task.Task.task_id == task_id)).all()
    if tasks is None or len(tasks) != 1:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"No task with {task_id} id."
        )

    task = tasks[0]
    for key, val in data_for_update.items():
        if not hasattr(task, key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to update task with ID {task_id}: "
                       f"field {key} if unknown."
            )
        # FIXME: data validation
        setattr(task, key, val)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task_by_id(task_id: int,
                      session: Session = Depends(get_session)):
    tasks = session.exec(select(schema_task.Task).where(schema_task.Task.task_id == task_id)).all()
    if tasks is None or len(tasks) != 1:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"No task with {task_id} id."
        )
    session.delete(tasks[0])
    session.commit()
