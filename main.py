from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
import auth, post, category, comment, tag, user
from auth import get_current_user
import models
from database import SessionLocal, engine, get_db
from models import User
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
app.include_router(auth.router)
app.include_router(post.router)
app.include_router(category.router)
app.include_router(comment.router)
app.include_router(tag.router)
app.include_router(user.router)

models.Base.metadata.create_all(bind=engine)
CLIENT_URL = os.environ.get("CLIENT_URL")
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[User, Depends(get_current_user)]


# @app.get("/", status_code=status.HTTP_200_OK)
# async def user(user: user_dependency):
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
#         )
#     return {"User": user}
