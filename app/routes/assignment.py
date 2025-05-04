from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from ..schemas import schemas
from typing import Annotated, List
from ..logic.auth import get_current_user

router = APIRouter(prefix="/assignment", tags=["Назначенные задачи"])

@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schemas.Assignment)
def create_assignment(assignment: schemas.Assignment,
                      current_user: Annotated[schemas.User, Depends(get_current_user)],
                      session: Session = Depends(get_session)):
    statement = (select(schemas.User)
                 .where(schemas.User.user_id == assignment.user_id))
    existing_user = session.exec(statement).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {assignment.user_id} not found"
        )

    statement = (select(schemas.Task)
                 .where(schemas.Task.task_id == assignment.task_id))
    existing_task = session.exec(statement).first()

    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {assignment.task_id} not found"
        )
    
    if existing_task.needed_role != existing_user.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can't assign {existing_task.needed_role} task to {existing_user.role} user"
        )
    
    new_assignment = schemas.Assignment(
        user_id = assignment.user_id,
        task_id = assignment.task_id
    )

    try:
        session.add(new_assignment)
        existing_user.workload += existing_task.estimated_time
        session.add(existing_user)
        session.commit()
        session.refresh(new_assignment)
        return new_assignment
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {assignment.task_id} already assigned"
        )

@router.get("/", status_code=status.HTTP_200_OK,
            response_model=List[schemas.Assignment])
def read_assignments(current_user: Annotated[schemas.User, Depends(get_current_user)], session: Session = Depends(get_session)):
    assignments = session.exec(select(schemas.Assignment)).all()
    if assignments is None or len(assignments) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The assignment list is empty."
        )
    return assignments


@router.get("/{assignment_id}", status_code=status.HTTP_200_OK,
            response_model=schemas.Assignment)
def read_assignment_by_id(assignment_id: int,
                          current_user: Annotated[schemas.User, Depends(get_current_user)],
                          session: Session = Depends(get_session)):
    assignment = session.exec(select(schemas.Assignment).where(schemas.Assignment.assignment_id == assignment_id)).first()
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"No assignment with {assignment_id} id."
        )
    return assignment

@router.delete("/{assignment_id}", status_code=status.HTTP_200_OK)
def delete_assignment(assignment_id: int,
                      current_user: Annotated[schemas.User, Depends(get_current_user)],
                      session: Session = Depends(get_session)):
    assignment = session.exec(select(schemas.Assignment).where(schemas.Assignment.assignment_id == assignment_id)).first()
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"No assignment with {assignment_id} id."
        )
    
    task = session.exec(select(schemas.Task)
                        .where(schemas.Task.task_id == assignment.task_id)).first()
    user = session.exec(select(schemas.User)
                        .where(schemas.User.user_id == assignment.user_id)).first()
    user.workload -= task.estimated_time
    session.add(user)
    session.delete(assignment)
    session.commit()
