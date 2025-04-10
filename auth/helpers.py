from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import scoped_session
from jose import JWTError, jwt
from typing import Annotated, Literal

from db import get_db
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context, oauth2_scheme
from models import UserModel
from schemas import UserSchema, UserWithPasswordSchema


# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_username(
    db: Annotated[scoped_session, Depends(get_db)], username: str, type_: Literal["schema", "model"] = "schema"
) -> UserModel | UserWithPasswordSchema | None:
    user = db.query(UserModel).filter(UserModel.username == username).first()

    if user:
        if type_ == "model":
            return user

        return UserWithPasswordSchema.model_validate(user)


def get_user_by_id(db: Annotated[scoped_session, Depends(get_db)], user_id: int) -> UserSchema | None:
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()

    if user:
        return UserSchema.model_validate(user)


# Authenticate user
def authenticate_user(
    db: Annotated[scoped_session, Depends(get_db)], username: str, password: str
) -> UserSchema | None:
    user = get_user_by_username(db, username)

    if not user or not verify_password(password, user.password):
        return None

    assert isinstance(user, UserSchema), "User should be an instance of UserSchema"

    return user


async def get_current_user(
    db: Annotated[scoped_session, Depends(get_db)],
    token: str = Depends(oauth2_scheme),
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db=db, username=username, type_="model")

    if user is None:
        raise credentials_exception

    assert isinstance(user, UserModel), "User should be an instance of UserModel"

    return user
