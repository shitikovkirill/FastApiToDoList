import enum
from sqlmodel import SQLModel, Field, Column, Enum
from typing import Optional


class TaskStatus(str, enum.Enum):
    completed = "completed"
    not_completed = "not completed"


class TaskBase(SQLModel):
    name: str
    description: Optional[str] = None
    status: TaskStatus = Field(sa_column=Column(Enum(TaskStatus)))


class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)


class TaskCreate(TaskBase):
    pass
