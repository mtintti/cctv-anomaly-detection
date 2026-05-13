
from fastapi import APIRouter
from ..services.fintraffic import all_stations

routerstations= APIRouter(tags=["stations"], responses={404:{"description":"not found :<"}})


@routerstations.get("/stations")
async def allstations():
    data = await all_stations()
    return {"data": data}




