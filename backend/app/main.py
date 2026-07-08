from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api import camera, stations
from ..ml.api.predict import router
from .config import logmain
from .dependecies import shared_client_start, shared_client_close
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from .services.db.database import open_pool
from ..ml.segmentation.datasetPreparation.segmentation import ml_backend
from .schedules.scheduleAPI import start_timer


# client (httpx.AsyncClient) on laitettuna alkamaan kun appi alkaa,
# yield (stop) tapahtuu kun appi suljetaan. contextmanager:illa hallitaan lifecycle clientillä myöhemmin data injectionilla  (testit, docker?)
# Clientti jaetaan services/dependency.py:sta läpi projektin

@asynccontextmanager
async def lifespan(app: FastAPI):
    await shared_client_start()
    logmain()
    # start_timer()
    #ml_backend()
    await open_pool()
    yield
    await shared_client_close()


app = FastAPI(lifespan=lifespan)
app.include_router(camera.router)
app.include_router(stations.router)
app.include_router(router)

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"],  allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)


@app.get("/")
async def root():
    return {"message" : "hello, scaling our app upwards!!! hey from new one"}
