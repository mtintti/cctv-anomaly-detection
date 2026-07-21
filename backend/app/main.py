import uuid

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from .api import camera, stations
from ..ml.api.predict import router, get_prediction, prediction_processing
from .config import logmain, logger
from .dependecies import shared_client_start, shared_client_close
from contextlib import asynccontextmanager
from .services.db.database import open_pool

# client (httpx.AsyncClient) on laitettuna alkamaan kun appi alkaa,
# yield (stop) tapahtuu kun appi suljetaan. contextmanager:illa hallitaan lifecycle clientillä myöhemmin data injectionilla  (testit, docker?)
# Clientti jaetaan services/dependency.py:sta läpi projektin

@asynccontextmanager
async def lifespan(app: FastAPI):
    await shared_client_start()
    logmain()
    # start_timer()
    #ml_backend()
    await warmup_request()
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

async def warmup_request():
        try:
            scope = {
                "type": "http",
                "method": "POST",
                "path": "/predict",
                "headers": [(b"host", b"app.local")]
            }
            mock_request = Request(scope=scope)

            prewarm_urls = [
                'https://weathercam.digitraffic.fi/C1255902.jpg']

            '''
            response = await prediction_processing(
                generated_predictID=uuid.uuid4(),
                req=mock_request,
                file=[],
                url=prewarm_urls
            )

            logger.info(f"prewarm is successful! returned data: {response}")
            '''
            logger.info("prewarm is paused")

        except Exception:
            logger.error("Warmup error, ", exc_info=True)
