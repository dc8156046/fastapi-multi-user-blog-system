from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
import auth, post, category, comment, tag, user
from auth import get_current_user
from pydantic import BaseModel
import models
from database import SessionLocal, engine, get_db
from models import Contact
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


db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[User, Depends(get_current_user)]


class ContactCreate(BaseModel):
    name: str
    email: str
    message: str


class ContactResponse(BaseModel):
    message: str
    contact_id: int


# Contact form
@app.post(
    "/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED
)
async def contact(contact: ContactCreate, db: db_dependency):
    new_contact = Contact(
        name=contact.name, email=contact.email, message=contact.message
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return {"message": "success", "contact_id": new_contact.id}


# @app.get("/", status_code=status.HTTP_200_OK)
# async def user(user: user_dependency):
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
#         )
#     return {"User": user}
