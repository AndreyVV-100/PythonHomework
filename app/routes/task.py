"""CRUD routes for tasks"""

from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from ..schemas import schemas

router = APIRouter(prefix="/tasks", tags=["Управление задачами в БД"])


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schemas.TaskRead)
def create_task(task: schemas.TaskCreate,
                session: Session = Depends(get_session)):
    """Create new task"""
    new_task = schemas.Task(
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
            response_model=List[schemas.TaskRead])
def read_tasks(session: Session = Depends(get_session)):
    """Read all tasks"""
    tasks = session.exec(select(schemas.Task)).all()
    if tasks is None or len(tasks) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="The task list is empty."
        )
    return tasks


@router.get("/{task_id}", status_code=status.HTTP_200_OK,
            response_model=schemas.TaskRead)
def read_task_by_id(task_id: int,
                    session: Session = Depends(get_session)):
    """Read task by id"""
    task = session.exec(select(schemas.Task).where(schemas.Task.task_id == task_id)).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"No task with {task_id} id."
        )
    return task


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=schemas.TaskRead)
def update_task_by_id(task_id: int, data_for_update: dict,
                      session: Session = Depends(get_session)):
    """Update task by id"""
    task = session.exec(select(schemas.Task).where(schemas.Task.task_id == task_id)).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"No task with {task_id} id."
        )

    for key, val in data_for_update.items():
        if not hasattr(task, key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to update task with ID {task_id}: "
                       f"field {key} if unknown."
            )
        setattr(task, key, val)

    try:
        _ = schemas.TaskCreate(
            description = task.description,
            deadline = task.deadline,
            priority = task.priority,
            estimated_time = task.estimated_time,
            needed_role = task.needed_role.lower()
        )
    except Exception as e:
        raise HTTPException(
                  status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                  detail="Invalid data for update."
              ) from e

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task_by_id(task_id: int,
                      session: Session = Depends(get_session)):
    """Delete task by id"""
    task = session.exec(select(schemas.Task).where(schemas.Task.task_id == task_id)).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"No task with {task_id} id."
        )

    assignments = session.exec(select(schemas.Assignment)
                               .where(schemas.Assignment.task_id == task_id)).all()
    if assignments is not None:
        for assignment in assignments:
            session.delete(assignment)
    session.delete(task)
    session.commit()
