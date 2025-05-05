"""Task scheduler"""

from sqlmodel import Session, select
from ..schemas import schemas

def schedule_tasks(session: Session):
    """Distribute unassigned tasks between users"""
    unassigned_tasks = session.exec(select(schemas.Task)
                                    .outerjoin(schemas.Assignment,
                                               schemas.Task.task_id == schemas.Assignment.task_id)
                                    .where(schemas.Assignment.task_id is None)).all()
    if unassigned_tasks is None or len(unassigned_tasks) == 0:
        return

    users = session.exec(select(schemas.User)).all()
    if users is None or len(users) == 0:
        return

    for task in unassigned_tasks:
        best_user = None
        min_workload = float("inf")

        for user in users:
            if task.needed_role != user.role:
                continue

            if user.workload < min_workload:
                best_user = user
                min_workload = user.workload

        if best_user:
            best_user.workload += task.estimated_time
            session.add(schemas.Assignment(
                user_id = best_user.user_id,
                task_id = task.task_id
            ))

    session.add_all(users)
    session.commit()
