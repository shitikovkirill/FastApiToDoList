import json
from celery import Celery
import requests
from redis import Redis

from app.config import get_settings, get_weather_key

redis = Redis(host='localhost', port=6379, decode_responses=True)
app = Celery('tasks', broker='redis://localhost')


@app.task
def get_weather(latitude, longitude):
    settings = get_settings()
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&appid={settings.api_key}"
    )
    if response.status_code == 200:
        key = get_weather_key(latitude, longitude)
        data = response.json()

        redis.set(key, json.dumps({
            "description": data["weather"][0]["description"],
            "temperature": data["main"]["temp"]
        }))
    else:
        print("Error")
