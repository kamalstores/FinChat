from fastapi import APIRouter, Depends, HTTPException
from app.shared.dependencies import get_current_user
from app.schema.user import UserProfile
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/", response_model=UserProfile)
def profile(current_user: Session = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return UserProfile(username=current_user.username, role=current_user.role)