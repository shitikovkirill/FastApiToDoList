import pathlib
from functools import lru_cache
from pydantic import BaseModel, BaseSettings, constr





class Settings(BaseSettings):
    api_key: str


@lru_cache()
def get_settings():
    return Settings()

ROOT = pathlib.Path(__file__).parent.resolve()