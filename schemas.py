from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


# Схема для пользователя
class UserBaseSchema(BaseModel):
    username: str


class UserCreateSchema(UserBaseSchema):
    password: str


class UserSchema(UserBaseSchema):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithPasswordSchema(UserSchema):
    password: str

    class Config:
        from_attributes = True


# Схема для доски
class BoardBaseSchema(BaseModel):
    title: str
    user_id: int
    description: Optional[str] = None


class BoardCreateSchema(BoardBaseSchema):
    pass


class BoardSchema(BoardBaseSchema):
    board_id: int
    created_at: datetime
    statuses: List["StatusSchema"]
    tasks: List["TaskSchema"]
    shared_with: List["BoardAccessSchema"]

    class Config:
        from_attributes = True


# Схема для статуса задачи
class StatusBaseSchema(BaseModel):
    name: str


class StatusCreateSchema(StatusBaseSchema):
    pass


class StatusSchema(StatusBaseSchema):
    status_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Схема для задачи
class TaskBaseSchema(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreateSchema(TaskBaseSchema):
    status_id: int


class TaskSchema(TaskBaseSchema):
    task_id: int
    created_at: datetime

    status: "StatusSchema"
    comments: List["CommentSchema"]
    tags: List["TagSchema"]

    class Config:
        from_attributes = True


# Схема для доступа к доске
class BoardAccessBaseSchema(BaseModel):
    full_access: Optional[bool] = True


class BoardAccessCreateSchema(BoardAccessBaseSchema):
    pass


class BoardAccessSchema(BoardAccessBaseSchema):
    access_id: int
    granted_at: datetime

    user: "UserSchema"

    class Config:
        from_attributes = True


# Схема для комментария
class CommentBaseSchema(BaseModel):
    content: str


class CommentCreateSchema(CommentBaseSchema):
    pass


class CommentSchema(CommentBaseSchema):
    comment_id: int
    created_at: datetime

    user: "UserSchema"
    attachments: List["AttachmentSchema"]

    class Config:
        from_attributes = True


# Схема для вложения
class AttachmentBaseSchema(BaseModel):
    file_path: str


class AttachmentCreateSchema(AttachmentBaseSchema):
    pass


class AttachmentSchema(AttachmentBaseSchema):
    attachment_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Схема для тега
class TagBaseSchema(BaseModel):
    label: str
    # task_id: int


class TagCreateSchema(TagBaseSchema):
    pass


class TagSchema(TagBaseSchema):
    tag_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Схема для лога действий пользователя
class UserActionLogBaseSchema(BaseModel):
    action_description: str
    user_id: int


class UserActionLogCreateSchema(UserActionLogBaseSchema):
    pass


class UserActionLogSchema(UserActionLogBaseSchema):
    log_id: int
    created_at: datetime

    class Config:
        from_attributes = True
