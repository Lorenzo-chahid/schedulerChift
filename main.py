from fastapi import FastAPI, BackgroundTasks
from datetime import datetime, timedelta
from scheduler import update_contacts

app = FastAPI()

next_update_time = datetime.now() + timedelta(minutes=50)


async def background_task():
    global next_update_time
    while True:
        update_contacts()
        next_update_time = datetime.now() + timedelta(minutes=50)
        await asyncio.sleep(1)


@app.on_event("startup")
async def run_on_startup():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(background_task)


@app.get("/")
async def index():
    time_remaining = next_update_time - datetime.now()
    minutes, seconds = divmod(time_remaining.total_seconds(), 60)
    return {
        "message": f"Prochaine mise à jour dans {int(minutes)} minutes et {int(seconds)} secondes."
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
