from pydantic import BaseModel, Field
from typing import List, Optional, Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Comment, User, CommentImage, CommentLike
from auth import get_current_user, UserOut


router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)


# Schema for creating a comment
class CommentCreate(BaseModel):
    post_id: int
    content: str
    images: Optional[List[str]] = (
        []
    )  # List of image URLs for simplicity; could be file uploads in a real application

    class Config:
        from_attributes = (
            True  # Enables compatibility with ORM objects like SQLAlchemy models
        )


# Schema for outputting comment data
class CommentDetailOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    images: List[str]  # List of image URLs associated with the comment
    likes_count: int  # Number of likes on the comment
    user: UserOut  # User who created the comment

    class Config:
        from_attributes = True


# Schema for outputting comment data
class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for updating a comment
class CommentUpdate(BaseModel):
    content: Optional[str] = None
    images: Optional[List[str]] = []  # New list of image URLs for the comment

    class Config:
        from_attributes = True


db_dependency = Annotated[Session, Depends(get_db)]


# Get all comments by post ID
@router.get(
    "/post/{post_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK
)
async def get_comments_by_post_id(post_id: int, db: db_dependency):
    comments = (
        db.query(Comment)
        .join(User, Comment.user_id == User.id)
        .filter(Comment.post_id == post_id, Comment.parent_id == None)
        .all()
    )

    return comments


user_dependency = Annotated[User, Depends(get_current_user)]


# Get comments created by the current user
@router.get("/", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
async def get_curent_user_comments(db: db_dependency, user: user_dependency):
    comments = db.query(Comment).filter(Comment.user_id == user.id).all()
    return comments


# get comments for a specific post
@router.get(
    "/{post_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK
)
async def get_post_comments(
    post_id: int,
    db: db_dependency,
):
    # Fetch comments for a specific post
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments


# Update a comment
@router.put("/{comment_id}", response_model=CommentOut, status_code=status.HTTP_200_OK)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: db_dependency,
    user: user_dependency,
):
    # Retrieve the comment by ID
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if comment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment",
        )

    # Update comment content if provided
    if comment_update.content:
        comment.content = comment_update.content
        comment.updated_at = datetime.now()

    # Update images if provided
    if comment_update.images:
        comment.images = [CommentImage(image_url=url) for url in comment_update.images]

    db.commit()
    db.refresh(comment)
    return comment


# Delete a comment
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: db_dependency,
    user: user_dependency,
):
    # Retrieve the comment by ID
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if comment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    db.delete(comment)
    db.commit()
    return None


# Like a comment
@router.post("/{comment_id}/like", status_code=status.HTTP_200_OK)
async def like_comment(
    comment_id: int,
    db: db_dependency,
    user: user_dependency,
):
    # Check if the comment exists
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    # Check if the user has already liked the comment
    if (
        db.query(CommentLike)
        .filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user.id)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this comment",
        )

    # Create a new like
    like = CommentLike(comment_id=comment_id, user_id=user.id)
    db.add(like)
    db.commit()
    return {"message": "Comment liked successfully"}


# Unlike a comment
@router.delete("/{comment_id}/like", status_code=status.HTTP_200_OK)
async def unlike_comment(
    comment_id: int,
    db: db_dependency,
    user: user_dependency,
):
    # Check if the comment exists
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    # Check if the user has liked the comment
    like = (
        db.query(CommentLike)
        .filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user.id)
        .first()
    )
    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not liked this comment",
        )

    # Delete the like
    db.delete(like)
    db.commit()
    return {"message": "Comment unliked successfully"}


# Get likes for a comment
@router.get("/{comment_id}/likes", status_code=status.HTTP_200_OK)
async def get_comment_likes(
    comment_id: int,
    db: db_dependency,
):
    # Check if the comment exists
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    # Get likes for the comment
    likes = db.query(CommentLike).filter(CommentLike.comment_id == comment_id).all()
    return likes.count()


# Get comments liked by the user
@router.get("/liked", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
async def get_liked_comments(
    db: db_dependency,
    user: user_dependency,
):
    # Get comments liked by the user
    liked_comments = (
        db.query(Comment).join(CommentLike).filter(CommentLike.user_id == user.id).all()
    )
    return liked_comments


# Create a new comment for a post
@router.post(
    "/post/{post_id}", response_model=CommentOut, status_code=status.HTTP_201_CREATED
)
async def create_comment_for_post(
    post_id: int,
    comment: CommentCreate,
    db: db_dependency,
    user: user_dependency,
):
    # Create a new comment
    new_comment = Comment(
        content=comment.content,
        user_id=user.id,
        post_id=post_id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


# Reply to a comment
@router.post(
    "/{comment_id}/reply",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def reply_to_comment(
    comment_id: int,
    comment: CommentCreate,
    db: db_dependency,
    user: user_dependency,
):
    # Retrieve the parent comment
    parent_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not parent_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    # Create a new comment
    new_comment = Comment(
        content=comment.content,
        user_id=user.id,
        parent_id=comment_id,
        post_id=parent_comment.post_id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


# Get replies for a comment
@router.get(
    "/{comment_id}/replies",
    response_model=List[CommentOut],
    status_code=status.HTTP_200_OK,
)
async def get_comment_replies(
    comment_id: int,
    db: db_dependency,
):
    # Fetch replies for a specific comment
    replies = db.query(Comment).filter(Comment.parent_id == comment_id).all()
    return replies
