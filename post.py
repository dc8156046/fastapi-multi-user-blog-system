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
    prefix="/posts",
    tags=["posts"],
)

# Schema for creating a post
class PostCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None  # Category may be optional
    is_published: bool = False
    slug: Optional[str] = None
    tags: Optional[List[int]] = []  # List of tag IDs
    images: Optional[List[str]] = []  # List of image URLs for simplicity; could be file uploads in a real application

    class Config:
        from_attributes = True  # Enables compatibility with ORM objects like SQLAlchemy models
    

# Schema for outputting post data
class PostOut(BaseModel):
    id: int
    title: str
    content: str
    category_id: Optional[int]
    user_id: int
    published_at: Optional[datetime] = None
    is_published: bool
    slug: str
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[str]] = []  # List of tag names
    images: List[str]  # List of image URLs

    class Config:
        from_attributes = True

# Schema for updating a post
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    is_published: Optional[bool] = None
    slug: Optional[str] = None
    tags: Optional[List[int]] = []
    images: Optional[List[str]] = []

    class Config:
        from_attributes = True

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

# Create a new post
@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: db_dependency, user: user_dependency):
    # Create Post instance
    new_post = Post(
        title=post.title,
        content=post.content,
        category_id=post.category_id,
        user_id=user.id,
        is_published=post.is_published,
        slug=post.slug
    )
    
    # Add tags
    if post.tags:
        tags = db.query(Tag).filter(Tag.id.in_(post.tags)).all()
        new_post.tags = tags

    # Add images
    for image_url in post.images:
        new_post.images.append(PostImage(image_url=image_url))

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# Get current user's all posts
@router.get("/", response_model=List[PostOut])
async def get_posts(db: db_dependency, user: user_dependency, skip: int = 0, limit: int = 10):
    posts = db.query(Post).filter(Post.user_id == user.id).offset(skip).limit(limit).all()
    return posts

# Get a post by ID
@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: db_dependency, user: user_dependency):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

# Update a post by ID
@router.put("/{post_id}", response_model=PostOut)
async def update_post(post_id: int, post: PostUpdate, db: db_dependency, user: user_dependency):
    post_instance = db.query(Post).get(post_id)
    if post_instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Check if the user is the author of the post
    if post_instance.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the author of this post")
    
    # Update the post
    if post.title is not None:
        post_instance.title = post.title
    if post.content is not None:
        post_instance.content = post.content
    if post.category_id is not None:
        post_instance.category_id = post.category_id
    if post.is_published is not None:
        post_instance.is_published = post.is_published
    if post.slug is not None:
        post_instance.slug = post.slug
    
    # Update tags
    if post.tags is not None:
        tags = db.query(Tag).filter(Tag.id.in_(post.tags)).all()
        post_instance.tags = tags

    # Update images
    if post.images is not None:
        post_instance.images = [PostImage(image_url=image_url) for image_url in post.images]

    post_instance.updated_at = datetime.now()
    db.commit()
    db.refresh(post_instance)
    return post_instance

# Delete a post by ID
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: db_dependency, user: user_dependency):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()
    return

# Publish a post by ID
@router.post("/{post_id}/publish", response_model=PostOut)
async def publish_post(post_id: int, db: db_dependency, user: user_dependency):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.is_published = True
    post.published_at = datetime.now()
    db.commit()
    db.refresh(post)
    return post

# Unpublish a post by ID
@router.post("/{post_id}/unpublish", response_model=PostOut)
async def unpublish_post(post_id: int, db: db_dependency, user: user_dependency):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.is_published = False
    post.published_at = None
    db.commit()
    db.refresh(post)
    return post

# Like a post by ID
@router.post("/{post_id}/like", response_model=PostOut)
async def like_post(post_id: int, db: db_dependency, user: user_dependency):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.likes.append(user)
    db.commit()
    db.refresh(post)

    return post

# Unlike a post by ID
@router.post("/{post_id}/unlike", response_model=PostOut)
async def unlike_post(post_id: int, db: db_dependency, user: user_dependency):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.likes.remove(user)
    db.commit()
    db.refresh(post)

    return post

# Get all posts
@router.get("/all", response_model=List[PostOut])
async def get_all_posts(db: db_dependency, skip: int = 0, limit: int = 10):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts

# Get all published posts
@router.get("/published", response_model=List[PostOut])
async def get_published_posts(db: db_dependency, skip: int = 0, limit: int = 10):
    posts = db.query(Post).filter(Post.is_published == True).offset(skip).limit(limit).all()
    return posts
