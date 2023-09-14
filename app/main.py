from fastapi import FastAPI, Depends
from sqlmodel import select, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session, init_db
from app.models import Task, TaskCreate


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/tasks", response_model=list[Task])
async def get_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task))
    tasks = result.scalars().all()
    return [Task(name=task.name, id=task.id) for task in tasks]


@app.post("/tasks")
async def add_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    task = Task.from_orm(task)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
