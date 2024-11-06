from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Post, User, Tag, PostImage
from auth import get_current_user

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)


# Schema for creating a tag
class TagCreate(BaseModel):
    name: str

    class Config:
        from_attributes = (
            True  # Enables compatibility with ORM objects like SQLAlchemy models
        )


# Schema for outputting tag data
class TagOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# Schema for updating a tag
class TagUpdate(BaseModel):
    name: Optional[str] = None

    class Config:
        from_attributes = True


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=List[TagOut], status_code=status.HTTP_200_OK)
async def get_tags(db: db_dependency, user: user_dependency):
    tags = db.query(Tag).filter(Tag.user_id == user.id).all()
    return tags


@router.post("/", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: TagCreate, db: db_dependency, user: user_dependency):
    new_tag = Tag(name=tag.name, user_id=user.id)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.get("/{tag_id}", response_model=TagOut, status_code=status.HTTP_200_OK)
async def get_tag(tag_id: int, db: db_dependency, user: user_dependency):
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user.id).first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.put("/{tag_id}", response_model=TagOut, status_code=status.HTTP_200_OK)
async def update_tag(
    tag_id: int, tag: TagUpdate, db: db_dependency, user: user_dependency
):
    tag_instance = (
        db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user.id).first()
    )
    if tag_instance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    for key, value in tag.dict(exclude_unset=True).items():
        setattr(tag_instance, key, value)

    db.commit()
    db.refresh(tag_instance)
    return tag_instance


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: db_dependency, user: user_dependency):
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user.id).first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    db.delete(tag)
    db.commit()
    return
