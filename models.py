from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, String, Text, DateTime, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(100))  # Хранить хэш пароля
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    boards: Mapped[List["BoardModel"]] = relationship(back_populates="user")
    comments: Mapped[List["CommentModel"]] = relationship(back_populates="user")
    shared_boards: Mapped[List["BoardAccessModel"]] = relationship(back_populates="user")
    action_logs: Mapped[List["UserActionLogModel"]] = relationship(back_populates="user")

    def has_access_to_board(self, board_id: int):
        return any([access.board_id == board_id for access in self.shared_boards])

    def is_owner_board(self, board_id: int):
        return any([board.board_id == board_id for board in self.boards])

    def has_assess_or_owner_board(self, board_id: int):
        return self.has_access_to_board(board_id) or self.is_owner_board(board_id)


class BoardModel(Base):
    __tablename__ = "boards"

    board_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="boards")
    statuses: Mapped[List["StatusModel"]] = relationship(back_populates="board")
    tasks: Mapped[List["TaskModel"]] = relationship(back_populates="board")
    shared_with: Mapped[List["BoardAccessModel"]] = relationship(back_populates="board")


class StatusModel(Base):
    __tablename__ = "statuses"

    status_id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.board_id"))
    name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    board: Mapped["BoardModel"] = relationship(back_populates="statuses")
    tasks: Mapped[List["TaskModel"]] = relationship(back_populates="status")


class TaskModel(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.board_id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status_id: Mapped[Optional[int]] = mapped_column(ForeignKey("statuses.status_id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    board: Mapped["BoardModel"] = relationship(back_populates="tasks")
    status: Mapped[Optional["StatusModel"]] = relationship(back_populates="tasks")
    comments: Mapped[List["CommentModel"]] = relationship(back_populates="task")
    tags: Mapped[List["TagModel"]] = relationship(back_populates="task")


class BoardAccessModel(Base):
    __tablename__ = "board_access"

    access_id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.board_id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    granted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    full_access: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    board: Mapped["BoardModel"] = relationship(back_populates="shared_with")
    user: Mapped["UserModel"] = relationship(back_populates="shared_boards")


class CommentModel(Base):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.task_id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    task: Mapped["TaskModel"] = relationship(back_populates="comments")
    user: Mapped["UserModel"] = relationship(back_populates="comments")
    attachments: Mapped[List["AttachmentModel"]] = relationship(back_populates="comment")


class AttachmentModel(Base):
    __tablename__ = "attachments"

    attachment_id: Mapped[int] = mapped_column(primary_key=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.comment_id"))
    file_path: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    comment: Mapped["CommentModel"] = relationship(back_populates="attachments")


class TagModel(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.task_id"))
    label: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    task: Mapped["TaskModel"] = relationship(back_populates="tags")


class UserActionLogModel(Base):
    __tablename__ = "user_action_logs"

    log_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    action_description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="action_logs")
