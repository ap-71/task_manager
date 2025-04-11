from enum import Enum
from typing import List, Annotated
from fastapi import Depends
from crud import BoardCRUD
from init import app
from schemas import (
    BoardAccessCreateSchema,
    BoardAccessSchema,
    BoardSchema,
    BoardCreateSchema,
    BoardUpdateSchema,
    CommentSchema,
    CommentCreateSchema,
    StatusSchema,
    StatusCreateSchema,
    StatusUpdateSchema,
    TaskSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
)

class Tags:
    board_access: List[str | Enum] = ["Board access"]
    board: List[str | Enum] = ["Board"]
    status: List[str | Enum] = ["Status"]
    task: List[str | Enum] = ["Task"]
    comment: List[str | Enum] = ["Comment"]


@app.post("/boards/{board_id}/accesses/", tags=Tags.board_access)
def create_board_access(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    board_access: BoardAccessCreateSchema, 
):
    return crud.shared(board_id=board_id, board_access=board_access)


@app.get("/boards/{board_id}/accesses/", response_model=List[BoardAccessSchema], tags=Tags.board_access)
def read_board_accesses(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return crud.access.get_all(board_id, skip=skip, limit=limit)


@app.delete("/boards/{board_id}/accesses/", tags=Tags.board_access)
def delete_board_access(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    access_id: int,
):
    return crud.access.delete(board_id=board_id, access_id=access_id)


@app.post("/boards/", response_model=BoardSchema, tags=Tags.board)
def create_board(board: BoardCreateSchema, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    return crud.create(board)


@app.get("/boards/", response_model=List[BoardSchema], tags=Tags.board)
def read_boards(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    skip: int = 0,
    limit: int = 100,
):
    return crud.get_all(skip=skip, limit=limit)


@app.get("/boards/{board_id}", response_model=BoardSchema, tags=Tags.board)
def read_board(board_id: int, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    return crud.get(board_id)


@app.delete("/boards/{board_id}", tags=Tags.board)
def delete_board(board_id: int, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]):
    return crud.delete(board_id=board_id)


@app.put("/boards/{board_id}", response_model=BoardSchema, tags=Tags.board)
def update_board(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    board: BoardUpdateSchema,
):
    return crud.update(board_id=board_id, data=board)


@app.post("/boards/{board_id}/statuses/", response_model=StatusSchema, tags=Tags.status)
def create_status(
    status: StatusCreateSchema,
    board_id: int,
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
):
    return crud.add_status(board_id=board_id, status=status)


@app.get("/boards/{board_id}/statuses/", response_model=List[StatusSchema], tags=Tags.status)
def read_statuses(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return crud.status.get_all(board_id=board_id, skip=skip, limit=limit)


@app.get("/boards/{board_id}/statuses/{status_id}", response_model=List[StatusSchema], tags=Tags.status)
def read_status(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    status_id: int,
):
    return crud.status.get(board_id=board_id, status_id=status_id)


@app.delete("/boards/{board_id}/statuses/{status_id}", response_model=List[StatusSchema], tags=Tags.status)
def delete_status_by_id(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    status_id: int,
):
    return crud.status.delete(board_id=board_id, status_id=status_id)


@app.put("/boards/{board_id}/statuses/{status_id}", response_model=List[StatusSchema], tags=Tags.status)
def update_status(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    status_id: int,
    status: StatusUpdateSchema,
):
    return crud.status.update(board_id=board_id, status_id=status_id, data=status)


@app.post("/boards/{board_id}/tasks/", response_model=TaskSchema, tags=Tags.task)
def create_task(
    task: TaskCreateSchema,
    board_id: int,
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
):
    return crud.add_task(board_id, task)


@app.get("/boards/{board_id}/tasks/", response_model=List[TaskSchema], tags=Tags.task)
def read_tasks(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return crud.task.get_all(board_id=board_id, skip=skip, limit=limit)


@app.get("/boards/{board_id}/tasks/{task_id}", response_model=List[TaskSchema], tags=Tags.task)
def read_task(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    task_id: int,
):
    return crud.task.get(board_id=board_id, task_id=task_id)


@app.delete("/boards/{board_id}/tasks/{task_id}", response_model=List[TaskSchema], tags=Tags.task)
def delete_task(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    task_id: int,
):
    return crud.task.delete(board_id=board_id, task_id=task_id)


@app.put("/boards/{board_id}/tasks/{task_id}", response_model=List[TaskSchema], tags=Tags.task)
def update_task(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    task_id: int,
    task: TaskUpdateSchema,
):
    return crud.task.update(board_id=board_id, task_id=task_id, data=task)


@app.post("/boards/{board_id}/tasks/{task_id}/comments/", response_model=CommentSchema, tags=Tags.comment)
def create_comment(
    board_id: int, task_id: int, comment: CommentCreateSchema, crud: Annotated[BoardCRUD, Depends(BoardCRUD)]
):
    return crud.task.add_comment(board_id=board_id, task_id=task_id, comment=comment)


@app.get("/boards/{board_id}/tasks/{task_id}/comments/", response_model=List[CommentSchema], tags=Tags.comment)
def read_comments(
    crud: Annotated[BoardCRUD, Depends(BoardCRUD)],
    board_id: int,
    task_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return crud.task.comment.get_all(board_id=board_id, task_id=task_id, skip=skip, limit=limit)
