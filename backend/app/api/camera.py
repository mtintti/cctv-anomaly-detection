# from http.client import responses
# from backend.app.main import app
import httpx
from fastapi import APIRouter, Depends
from ..dependecies import get_shared_client
from ..services.fintraffic import camera_station

router = APIRouter(tags=["camera"], responses={404: {"description": "not found :<"}})

#Api route kutsutaan servicessä
@router.get("/camera/{camera_id}")
async def get_camera_frame(camera_id: str, client: httpx.AsyncClient = Depends(get_shared_client)):
    return await camera_station(camera_id, client)
