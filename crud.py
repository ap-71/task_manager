# CRUD operations
from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import Depends
from auth.helpers import get_current_user
from db import get_db
from models import BoardAccessModel, StatusModel, TagModel, TaskModel, UserModel, BoardModel, CommentModel
from schemas import BoardCreateSchema, CommentCreateSchema, StatusCreateSchema, TaskCreateSchema, UserCreateSchema


class CRUD:
    def __init__(
        self,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ):
        self.db = db
        self.current_user = current_user


class StatusCRUD(CRUD):
    def get_status(self, board_id: int, status_id: int):
        if self.current_user.has_assess_or_owner_board(board_id):
            return self.db.query(StatusModel).filter(StatusModel.status_id == status_id).first()
        else:
            return None

    def get_statuses(self, board_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(StatusModel).filter(StatusModel.board_id == board_id).offset(skip).limit(limit).all()

    def create_status(self, status: StatusCreateSchema, board_id: int):
        db_status = StatusModel(name=status.name, board_id=board_id)
        self.db.add(db_status)
        self.db.commit()
        self.db.refresh(db_status)
        return db_status


class CommentCRUD(CRUD):
    def get_comment(self, board_id: int, task_id, comment_id: int):
        if self.current_user.has_assess_or_owner_board(board_id):
            return (
                self.db.query(CommentModel)
                .filter(CommentModel.comment_id == comment_id, CommentModel.task_id == task_id)
                .first()
            )
        else:
            return None

    def get_comments(self, board_id: int, task_id: int, skip: int = 0, limit: int = 100):
        return (
            self.db.query(CommentModel)
            .filter(CommentModel.task_id == task_id, CommentModel.task.board_id == board_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_comment(self, comment: CommentCreateSchema):
        db_comment = CommentModel(content=comment.content, task_id=comment.task_id, user_id=self.current_user.user_id)
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment


class TaskCRUD(CRUD):
    def __init__(
        self,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ):
        self.comment_crud: CommentCRUD = CommentCRUD(db=db, current_user=current_user)
        super().__init__(db, current_user)

    def get_task(self, board_id: int, task_id: int):
        # Проверяем, есть ли у пользователя доступ к доске или он является ее владельцем
        if self.current_user.has_assess_or_owner_board(board_id):
            return self.db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
        else:
            return None

    def get_tasks(self, board_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(TaskModel).filter(TaskModel.board_id == board_id).offset(skip).limit(limit).all()

    def create_task(self, board_id: int, task: TaskCreateSchema):
        db_task = TaskModel(title=task.title, description=task.description, board_id=board_id, status_id=task.status_id)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def add_comment_to_task(self, board_id: int, task_id: int, comment: CommentModel):
        task = self.get_task(board_id=board_id, task_id=task_id)

        if task:
            task.comments.append(comment)

    def add_tag_to_task(self, board_id: int, task_id: int, tag: TagModel):
        task = self.get_task(board_id=board_id, task_id=task_id)

        if task:
            task.tags.append(tag)


class BoardCRUD(CRUD):
    def __init__(
        self,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ):
        self.status_crud: StatusCRUD = StatusCRUD(db=db, current_user=current_user)
        self.task_crud: TaskCRUD = TaskCRUD(db=db, current_user=current_user)
        super().__init__(db, current_user)

    def get_board(self, board_id: int):
        if self.current_user.has_assess_or_owner_board(board_id):
            return self.db.query(BoardModel).filter(BoardModel.board_id == board_id).first()
        else:
            return None

    def get_boards(self, skip: int = 0, limit: int = 100) -> List[BoardModel]:
        return (
            self.db.query(BoardModel)
            .filter(BoardModel.user_id == self.current_user.user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_board(self, board: BoardCreateSchema) -> BoardModel:
        db_board = BoardModel(title=board.title, description=board.description, user_id=self.current_user.user_id)
        self.db.add(db_board)
        self.db.commit()
        self.db.refresh(db_board)
        return db_board

    def add_task_to_board(self, board_id: int, task: TaskModel):
        board = self.get_board(board_id=board_id)

        if board:
            board.tasks.append(task)

    def add_status_to_board(self, board_id: int, status: StatusModel):
        board = self.get_board(board_id=board_id)

        if board:
            board.statuses.append(status)

    def shared_board(self, board_id: int, user_id: int):
        board = self.get_board(board_id=board_id)

        if board:
            bam = BoardAccessModel(user_id=user_id, board_id=board_id)
            board.shared_with.append(bam)
            self.db.add(bam)
