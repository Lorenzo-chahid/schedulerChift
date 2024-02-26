from fastapi import FastAPI, BackgroundTasks
from datetime import datetime, timedelta
import asyncio  # N'oubliez pas d'importer asyncio

from scheduler import (
    update_contacts,
)  # Assurez-vous que update_contacts est une coroutine asynchrone

app = FastAPI()

next_update_time = datetime.now() + timedelta(minutes=1)  # Mise à jour pour une minute


async def background_task():
    global next_update_time
    while True:
        await update_contacts()  # Assurez-vous que cette fonction est asynchrone ou utilisez run_in_executor pour les fonctions synchrones
        next_update_time = datetime.now() + timedelta(
            minutes=1
        )  # Mise à jour pour une minute
        await asyncio.sleep(60)  # Attend 60 secondes avant de réexécuter


@app.on_event("startup")
async def run_on_startup():
    asyncio.create_task(
        background_task()
    )  # Créez la tâche d'arrière-plan sans bloquer le démarrage


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
