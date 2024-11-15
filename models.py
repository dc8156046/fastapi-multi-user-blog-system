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
    avatar = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Establish relationship with the Post model
    posts = relationship("Post", back_populates="author")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(
        Integer, ForeignKey("categories.id"), default=0, nullable=True, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Establish relationship with the Post model
    posts = relationship("Post", back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Establish relationship with the Post model
    posts = relationship("PostTag", back_populates="tags")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, default=datetime)
    slug = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    images = relationship("PostImage", back_populates="posts")
    tags = relationship("PostTag", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

    # Establish relationship with the Post model
    posts = relationship("Post", back_populates="tags")
    tags = relationship("Tag", back_populates="posts")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    parent_id = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime)

    # Relationships

    post = relationship("Post", back_populates="comments")
    images = relationship(
        "CommentImage", back_populates="comment", cascade="all, delete-orphan"
    )
    likes = relationship(
        "CommentLike", back_populates="comment", cascade="all, delete-orphan"
    )


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime)
    updated_at = Column(DateTime, default=datetime, onupdate=datetime)

    # Establish relationship with the Post model
    post = relationship("Post", back_populates="likes")


class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime)
    updated_at = Column(DateTime, default=datetime, onupdate=datetime)

    # Establish relationship with the Comment model
    comment = relationship("Comment", back_populates="likes")


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime)
    updated_at = Column(DateTime, default=datetime, onupdate=datetime)


class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime)

    # Establish relationship with the Post model
    posts = relationship("Post", back_populates="images")


class CommentImage(Base):
    __tablename__ = "comment_images"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime)

    # Establish relationship with the Comment model
    comment = relationship("Comment", back_populates="images")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
