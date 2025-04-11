# CRUD operations
from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from auth.helpers import get_current_user
from db import get_db
from models import BoardAccessModel, StatusModel, TagModel, TaskModel, UserModel, BoardModel, CommentModel
from schemas import (
    BoardAccessCreateSchema,
    BoardCreateSchema,
    BoardUpdateSchema,
    CommentCreateSchema,
    StatusCreateSchema,
    StatusUpdateSchema,
    TagCreateSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
)


class CRUD:
    def __init__(
        self,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ):
        self.db = db
        self.current_user = current_user


class TagCRUD(CRUD):
    def get(self, board_id: int, tag_id: int):
        if self.current_user.has_assess_or_owner_board(board_id):
            return self.db.query(TagModel).filter(TagModel.tag_id == tag_id).first()
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tag not found")

    def get_all(self, tag_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(TagModel).filter(TagModel.tag_id == tag_id).offset(skip).limit(limit).all()

    def create(self, tag: TagCreateSchema, board_id: int):
        db_tag = TagModel(label=tag.label, board_id=board_id)
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag


class StatusCRUD(CRUD):
    def get(self, board_id: int, status_id: int):
        if self.current_user.has_assess_or_owner_board(board_id):
            record = self.db.query(StatusModel).filter(StatusModel.status_id == status_id).first()
            if record:
                return record
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    def get_all(self, board_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(StatusModel).filter(StatusModel.board_id == board_id).offset(skip).limit(limit).all()

    def create(self, status: StatusCreateSchema, board_id: int):
        db_status = StatusModel(name=status.name, board_id=board_id)
        self.db.add(db_status)
        self.db.commit()
        self.db.refresh(db_status)
        return db_status

    def delete(self, board_id: int, status_id: int):
        # CHECK IF USER HAS ACCESS TO THE BOARD
        status = self.get(board_id, status_id)
        self.db.delete(status)

    
    def update(self, board_id: int, status_id: int, data: StatusUpdateSchema):
        # CHECK IF USER HAS ACCESS TO THE BOARD
        status = self.get(board_id, status_id)
        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(status, field, value)
        
        return status

class CommentCRUD(CRUD):
    def get(self, board_id: int, task_id, comment_id: int):
        if self.current_user.has_assess_or_owner_board(board_id):
            record = (
                self.db.query(CommentModel)
                .filter(CommentModel.comment_id == comment_id, CommentModel.task_id == task_id)
                .first()
            )
            if record:
                return record
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    def get_all(self, board_id: int, task_id: int, skip: int = 0, limit: int = 100):
        return (
            self.db.query(CommentModel)
            .filter(CommentModel.task_id == task_id, CommentModel.task.board_id == board_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, task_id: int, comment: CommentCreateSchema):
        db_comment = CommentModel(content=comment.content, task_id=task_id, user_id=self.current_user.user_id)
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
        self.comment: CommentCRUD = CommentCRUD(db=db, current_user=current_user)
        self.tag: TagCRUD = TagCRUD(db=db, current_user=current_user)
        super().__init__(db, current_user)

    def get(self, board_id: int, task_id: int):
        # Проверяем, есть ли у пользователя доступ к доске или он является ее владельцем
        if self.current_user.has_assess_or_owner_board(board_id):
            record = self.db.query(TaskModel).filter(TaskModel.task_id == task_id).first()

            if record:
                return record
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    def get_all(self, board_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(TaskModel).filter(TaskModel.board_id == board_id).offset(skip).limit(limit).all()

    def create(self, board_id: int, task: TaskCreateSchema):
        db_task = TaskModel(title=task.title, description=task.description, board_id=board_id, status_id=task.status_id)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def add_comment(self, board_id: int, task_id: int, comment: CommentCreateSchema):
        task = self.get(board_id=board_id, task_id=task_id)

        comment_model = self.comment.create(task_id=task.task_id, comment=comment)
        task.comments.append(comment_model)
        self.db.commit()

    def add_tag(self, board_id: int, task_id: int, tag: TagCreateSchema):
        task = self.get(board_id=board_id, task_id=task_id)

        tag_model = self.tag.create(board_id=board_id, tag=tag)
        task.tags.append(tag_model)
        self.db.commit()
        
    def delete(self, board_id: int, task_id: int):
        # CHECK IF USER HAS ACCESS TO THE BOARD
        task = self.get(board_id=board_id, task_id=task_id)
        self.db.delete(task)
    
    def update(self, board_id: int, task_id: int, data: TaskUpdateSchema):
        # CHECK IF USER HAS ACCESS TO THE BOARD
        task = self.get(board_id=board_id, task_id=task_id)
        
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(task, field, value)

        return task

class BoardAccessCRUD(CRUD):
    def get(self, board_id: int, access_id: int):
        if self.current_user.has_assess_or_owner_board(board_id):
            record = self.db.query(BoardAccessModel).filter(BoardAccessModel.access_id == access_id).first()

            if record:
                return record
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    def get_all(self, board_id: int, skip: int = 0, limit: int = 100):
        return (
            self.db.query(BoardAccessModel)
            .filter(BoardAccessModel.board_id == board_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, board_id: int, user_id: int):
        record = self.db.query(BoardAccessModel).filter(BoardAccessModel.board_id == board_id, BoardAccessModel.user_id == user_id).first()
        
        if record is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access already exists")
        
        db_board_access = BoardAccessModel(user_id=user_id, board_id=board_id)
        
        self.db.add(db_board_access)
        self.db.commit()
        self.db.refresh(db_board_access)
        
        return db_board_access
    
    def delete(self, board_id: int, access_id: int):
        # CHECK IF USER HAS ACCESS TO THE BOARD
        self.db.query(BoardAccessModel).filter(BoardAccessModel.board_id == board_id, BoardAccessModel.access_id == access_id).delete()


class BoardCRUD(CRUD):
    def __init__(
        self,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ):
        self.status: StatusCRUD = StatusCRUD(db=db, current_user=current_user)
        self.task: TaskCRUD = TaskCRUD(db=db, current_user=current_user)
        self.access: BoardAccessCRUD = BoardAccessCRUD(db=db, current_user=current_user)
        super().__init__(db, current_user)

    def get(self, board_id: int):
        if self.current_user.has_assess_or_owner_board(board_id):
            record = self.db.query(BoardModel).filter(BoardModel.board_id == board_id).first()

            if record:
                return record
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    def get_all(self, skip: int = 0, limit: int = 100) -> List[BoardModel]:
        return (
            self.db.query(BoardModel)
            .filter(BoardModel.user_id == self.current_user.user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, board: BoardCreateSchema) -> BoardModel:
        db_board = BoardModel(title=board.title, description=board.description, user_id=self.current_user.user_id)
        self.db.add(db_board)
        self.db.commit()
        self.db.refresh(db_board)

        return db_board

    def add_task(self, board_id: int, task: TaskCreateSchema):
        board = self.get(board_id=board_id)

        self.task.create(board_id=board.board_id, task=task)

    def add_status(self, board_id: int, status: StatusCreateSchema):
        board = self.get(board_id=board_id)

        self.status.create(board_id=board.board_id, status=status)

    def shared(self, board_id: int, board_access: BoardAccessCreateSchema):
        board = self.get(board_id=board_id)

        self.access.create(board_id=board.board_id, user_id=board_access.user_id)

    def delete(self, board_id: int):
        # CHECK IF USER HAS ACCESS TO THE BOARD
        res = self.db.query(BoardModel).filter(BoardModel.board_id == board_id, BoardModel.user_id == self.current_user.user_id).delete()
        
        if res == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Невозможно удалить доску")
    
    def update(self, board_id: int, data: BoardUpdateSchema):
        # CHECK IF USER HAS ACCESS TO THE BOARD
        board = self.get(board_id=board_id)
        
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(board, field, value)
        
        return board