from typing import List, Annotated
from fastapi import Depends, HTTPException
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
def create_board_api(board: BoardCreateSchema, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    return crud.create(board)


@app.get("/boards/", response_model=List[BoardSchema])
def read_boards(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    skip: int = 0,
    limit: int = 100,
):
    boards = crud.get_all(skip=skip, limit=limit)
    return boards


@app.get("/boards/{board_id}", response_model=BoardSchema)
def read_board(board_id: int, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    board = crud.get(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@app.post("/statuses/", response_model=StatusSchema)
def create_status_api(
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
    statuses = crud.status.get_all(board_id=board_id, skip=skip, limit=limit)
    return statuses


@app.post("/tasks/", response_model=TaskSchema)
def create_task_api(
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
    tasks = crud.task.get_all(board_id=board_id, skip=skip, limit=limit)
    return tasks


@app.post("/comments/", response_model=CommentSchema)
def create_comment_api(
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
