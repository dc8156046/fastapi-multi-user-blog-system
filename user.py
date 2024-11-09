from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Post, User
from auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

db_dependency = Annotated[Session, Depends(get_db)]


# Schema for showing user data
class UserOut(BaseModel):
    id: int
    username: str
    avatar: str
    bio: str

    class Config:
        from_attributes = True


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: db_dependency):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
