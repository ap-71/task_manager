from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import scoped_session

from db import get_db
from .helpers import (
    authenticate_user,
    get_current_user,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from schemas import UserSchema, UserCreateSchema, UserWithPasswordSchema
from models import UserModel
from init import app


# Token route
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: scoped_session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


# Protect routes with authentication
@app.get("/users/me", response_model=UserSchema)
async def read_users_me(user: UserModel = Depends(get_current_user)):
    return UserSchema.model_validate(user)


# Registration route
@app.post("/register", response_model=UserSchema)
def register_user(user: UserCreateSchema, db: scoped_session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(username=user.username, password=hashed_password)  # Use hashed password

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
