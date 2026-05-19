from fastapi import APIRouter, Depends, HTTPException
from app.schemas import CurrentUser
from app.dependencies import require_admin, get_storage
from app.storage import Storage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    _: CurrentUser = Depends(require_admin),
    store: Storage = Depends(get_storage),
):
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    for task in store.tasks.values():
        by_status[task.status] += 1
    return {"total_tasks": len(store.tasks), "by_status": by_status}


@router.delete("/tasks/{task_id}", status_code=204)
def admin_delete_task(
    task_id: int,
    _: CurrentUser = Depends(require_admin),
    store: Storage = Depends(get_storage),
):
    if task_id not in store.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del store.tasks[task_id]
