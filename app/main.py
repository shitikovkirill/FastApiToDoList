import json
import time

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import aioredis

from app.db import get_session, init_db
from app.models import Task, TaskCreate
from app.config import ROOT, get_weather_key
from app.tasks import get_weather as get_weather_task

redis = aioredis.from_url("redis://localhost")

app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory=f"{ROOT}/templates/static"),
    name="static"
)
templates = Jinja2Templates(directory=f"{ROOT}/templates")


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time*1000)
    return response


@app.get("/")
def index(
    request: Request,
):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Task list"}
    )


@app.get("/weather")
async def get_weather(
    latitude: float,
    longitude: float
):
    key = get_weather_key(latitude, longitude)
    weather_cache = await redis.get(key)
    if weather_cache is None:
        get_weather_task.delay(latitude, longitude)
        return {"status": "start process"}

    responce = {"status": "ok"}
    responce.update(json.loads(weather_cache))
    return responce


@app.get("/tasks", response_model=list[Task])
async def get_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task))
    tasks = result.scalars().all()
    return tasks


@app.post("/tasks")
async def add_task(
    task: TaskCreate,
    session: AsyncSession = Depends(get_session)
):
    task = Task.from_orm(task)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session)
):
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return {"ok": True}
