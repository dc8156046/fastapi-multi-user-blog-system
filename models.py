from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    avatar = Column(String)
    bio = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, default=datetime)
    slug = Column(String, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relationships
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="post_tags", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class PostTag(Base):
    __tablename__ = "post_tags"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"))

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relationships
    post = relationship("Post", back_populates="comments")
    images = relationship("CommentImage", back_populates="comment", cascade="all, delete-orphan")
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    image_url = Column(String)
    created_at = Column(DateTime)

class CommentImage(Base):
    __tablename__ = "comment_images"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    image_url = Column(String)
    created_at = Column(DateTime)
