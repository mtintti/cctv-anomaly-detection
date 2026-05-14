from fastapi import FastAPI
from .api import camera,stations
from .dependecies import shared_client_start,shared_client_close
from contextlib import asynccontextmanager

# client (httpx.AsyncClient) on laitettuna alkamaan kun appi alkaa,
# yield (stop) tapahtuu kun appi suljetaan. contextmanager:illa hallitaan lifecycle clientillä myöhemmin data injectionilla  (testit, docker?)
# Clientti jaetaan services/dependency.py:sta läpi projektin

@asynccontextmanager
async def lifespan(app: FastAPI):
    await shared_client_start()
    yield
    await shared_client_close()

app= FastAPI(lifespan=lifespan)

app.include_router(camera.router)
app.include_router(stations.router)

@app.get("/")
async def root():
    return {"message" : "hello, scaling our app upwards!!! hey from new one"}
