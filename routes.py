from typing import List, Annotated
from fastapi import Depends, HTTPException
from crud import BoardCRUD, TaskCRUD, StatusCRUD, CommentCRUD
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
def create_board_api(board: BoardCreateSchema, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    return crud.create_board(board)


@app.get("/boards/", response_model=List[BoardSchema])
def read_boards(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    skip: int = 0,
    limit: int = 100,
):
    boards = crud.get_boards(skip=skip, limit=limit)
    return boards


@app.get("/boards/{board_id}", response_model=BoardSchema)
def read_board(board_id: int, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    board = crud.get_board(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@app.post("/statuses/", response_model=StatusSchema)
def create_status_api(
    status: StatusCreateSchema,
    board_id: int,
    crud: Annotated[StatusCRUD, Depends(StatusCRUD)],
):
    return crud.create_status(status=status, board_id=board_id)


@app.get("/statuses/", response_model=List[StatusSchema])
def read_statuses(
    crud: Annotated[StatusCRUD, Depends(StatusCRUD)],
    board_id: int,
    skip: int = 0,
    limit: int = 100,
):
    statuses = crud.get_statuses(board_id=board_id, skip=skip, limit=limit)
    return statuses


@app.post("/tasks/", response_model=TaskSchema)
def create_task_api(
    task: TaskCreateSchema,
    board_id: int,
    crud: Annotated[TaskCRUD, Depends(TaskCRUD)],
):
    return crud.create_task(board_id, task)


@app.get("/tasks/", response_model=List[TaskSchema])
def read_tasks(
    crud: Annotated[TaskCRUD, Depends(TaskCRUD)],
    board_id: int,
    skip: int = 0,
    limit: int = 100,
):
    tasks = crud.get_tasks(board_id=board_id, skip=skip, limit=limit)
    return tasks


@app.post("/comments/", response_model=CommentSchema)
def create_comment_api(comment: CommentCreateSchema, crud: Annotated[CommentCRUD, Depends(CommentCRUD)]):
    return crud.create_comment(comment)


@app.get("/comments/", response_model=List[CommentSchema])
def read_comments(
    crud: Annotated[CommentCRUD, Depends(CommentCRUD)],
    board_id: int,
    task_id: int,
    skip: int = 0,
    limit: int = 100,
):
    comments = crud.get_comments(board_id=board_id, task_id=task_id, skip=skip, limit=limit)
    return comments
