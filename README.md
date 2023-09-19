# FastApiToDoList

### Install

* run redis `docker run --name celery-redis -p 6379:6379 -d redis`
* python -m venv venv
* source venv/bin/activate
* pip install -r requirements.txt
* uvicorn app.main:app --reload
* uvicorn app.main:app
* API_KEY=<key from openweathermap.org> celery -A app.tasks.app worker

### Usage
Go to `http://localhost:8000/`