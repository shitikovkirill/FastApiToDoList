import pathlib
from datetime import date
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    api_key: str


@lru_cache()
def get_settings():
    return Settings()


ROOT = pathlib.Path(__file__).parent.resolve()


def get_weather_key(latitude, longitude, ):
    today = date.today()
    return "{}_{}_{}".format(latitude, longitude, today)
