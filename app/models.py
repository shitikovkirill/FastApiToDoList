from sqlmodel import SQLModel, Field
from typing import Optional 

class TaskBase(SQLModel):
    name: str
    description: Optional[str] = None


class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)

class TaskCreate(TaskBase):
    pass