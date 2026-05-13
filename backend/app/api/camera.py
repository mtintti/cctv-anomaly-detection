#from http.client import responses
#from backend.app.main import app
from fastapi import APIRouter
from ..services.fintraffic import camera_station

routerCam= APIRouter(tags=["camera"], responses={404:{"description":"not found :<"}})

@routerCam.get("/camera/{camera_id}")
async def getcameraframe(camera_id :str):
    data = await camera_station(camera_id)
    print(data)
    return {"data": data}

