import time

import requests
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from sqlmodel import select, Session
from datetime import date
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session, init_db
from app.models import Task, TaskCreate
from app.config import ROOT, Settings, get_settings

weather_cache = {}

app = FastAPI()


app.mount("/static", StaticFiles(directory=f"{ROOT}/templates/static"), name="static")
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


@app.get("/weather")
def get_weather(
    latitude: float,
    longitude: float,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings)
):
    global weather_cache
    today = date.today()
    key=f"{latitude}_{longitude}_{today}"
    weather=weather_cache.get(key)
    if weather is None:
        weather_cache[key] = ...
        background_tasks.add_task(cache_weather, key, latitude, longitude, settings.api_key)
        return { "status": "start process" }
    elif weather == ...:
        return { "status": "processing" }
    responce = {"status": "ok"}
    responce.update(weather_cache[key])
    return responce

def cache_weather(key, latitude, longitude, api_key):
    global weather_cache
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&appid={api_key}"
    )
    if response.status_code == 200:
        data = response.json()
        weather_cache[key] = {
            "description": data["weather"][0]["description"],
            "temperature": data["main"]["temp"]
        }
    else:
        print("Error")


@app.get("/")
def index(
    request: Request,
):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Task list"}
    )


@app.get("/tasks", response_model=list[Task])
async def get_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task))
    tasks = result.scalars().all()
    return tasks


@app.post("/tasks")
async def add_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
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
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return {"ok": True}
