from fastapi import FastAPI
from .api import camera,stations

app = FastAPI()

app.include_router(camera.routerCam)
app.include_router(stations.routerstations)

@app.get("/")
async def root():
    return {"message" : "hello, scaling our app upwards!!! hey from new one"}
