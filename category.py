from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Category, User
from auth import get_current_user

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


# Schema for creating a category
class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = (
            True  # Enables compatibility with ORM objects like SQLAlchemy models
        )


# Schema for outputting category data
class CategoryOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    user_id: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for updating a category
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


db_dependency = Annotated[Session, Depends(get_db)]


# Get category by ID
@router.get(
    "/detail/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK
)
async def get_category(
    category_id: int,
    db: db_dependency,
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=List[CategoryOut], status_code=status.HTTP_200_OK)
async def get_categories(db: db_dependency, user: user_dependency):
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    return categories


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CategoryCreate, db: db_dependency, user: user_dependency
):
    category = Category(
        **request.dict(),
        user_id=user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get(
    "/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK
)
async def get_category(category_id: int, db: db_dependency, user: user_dependency):
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user.id)
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@router.put(
    "/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK
)
async def update_category(
    category_id: int, request: CategoryUpdate, db: db_dependency, user: user_dependency
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user.id)
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    for key, value in request.dict().items():
        setattr(category, key, value)
    category.updated_at = datetime.now()
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: db_dependency, user: user_dependency):
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user.id)
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    db.delete(category)
    db.commit()
    return


# get all categories
@router.get("/all", response_model=List[CategoryOut], status_code=status.HTTP_200_OK)
async def get_all_categories(db: db_dependency):
    categories = db.query(Category).all()
    return categories
