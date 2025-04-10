from typing import List, Annotated
from fastapi import Depends
from crud import BoardCRUD
from init import app
from schemas import (
    BoardSchema,
    BoardCreateSchema,
    CommentSchema,
    CommentCreateSchema,
    StatusSchema,
    StatusCreateSchema,
    TaskSchema,
    TaskCreateSchema,
)


@app.post("/boards/", response_model=BoardSchema)
def create_board(board: BoardCreateSchema, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    return crud.create(board)


@app.get("/boards/", response_model=List[BoardSchema])
def read_boards(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    skip: int = 0,
    limit: int = 100,
):
    return crud.get_all(skip=skip, limit=limit)


@app.get("/boards/{board_id}", response_model=BoardSchema)
def read_board(board_id: int, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    return crud.get(board_id)


@app.post("/statuses/", response_model=StatusSchema)
def create_status(
    status: StatusCreateSchema,
    board_id: int,
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
):
    return crud.add_status(board_id=board_id, status=status)

@app.get("/statuses/", response_model=List[StatusSchema])
def read_statuses(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return crud.status.get_all(board_id=board_id, skip=skip, limit=limit)


@app.post("/tasks/", response_model=TaskSchema)
def create_task(
    task: TaskCreateSchema,
    board_id: int,
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
):
    return crud.add_task(board_id, task)


@app.get("/tasks/", response_model=List[TaskSchema])
def read_tasks(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return crud.task.get_all(board_id=board_id, skip=skip, limit=limit)


@app.post("/comments/", response_model=CommentSchema)
def create_comment(
    board_id: int, task_id: int, comment: CommentCreateSchema, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]
):
    return crud.task.add_comment(board_id=board_id, task_id=task_id, comment=comment)


@app.get("/comments/", response_model=List[CommentSchema])
def read_comments(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    task_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return crud.task.comment.get_all(board_id=board_id, task_id=task_id, skip=skip, limit=limit)
