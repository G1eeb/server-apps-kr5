from fastapi import APIRouter, Depends
from app.schemas import CurrentUser
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return current_user


@router.get("/{user_id}")
def get_user(user_id: int, current_user: CurrentUser = Depends(get_current_user)):
    return {"id": user_id}
