from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from app.schemas import TaskCreate, TaskOut, TaskStatusUpdate, CurrentUser
from app.dependencies import get_current_user, get_storage
from app.storage import Storage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", status_code=201, response_model=TaskOut)
def create_task(
    task: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user),
    store: Storage = Depends(get_storage),
) -> TaskOut:
    task_id = store.next_id()
    new_task = TaskOut(
        id=task_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        owner_id=current_user.id,
    )
    store.tasks[task_id] = new_task
    return new_task


@router.get("", response_model=List[TaskOut])
def list_tasks(
    status: Optional[str] = None,
    min_priority: Optional[int] = None,
    current_user: CurrentUser = Depends(get_current_user),
    store: Storage = Depends(get_storage),
) -> List[TaskOut]:
    tasks = [t for t in store.tasks.values() if t.owner_id == current_user.id]
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if min_priority is not None:
        tasks = [t for t in tasks if t.priority >= min_priority]
    return tasks


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    store: Storage = Depends(get_storage),
) -> TaskOut:
    task = store.tasks.get(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    store: Storage = Depends(get_storage),
) -> TaskOut:
    task = store.tasks.get(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = task.model_copy(update={"status": body.status})
    store.tasks[task_id] = updated
    return updated


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    store: Storage = Depends(get_storage),
):
    task = store.tasks.get(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    del store.tasks[task_id]
