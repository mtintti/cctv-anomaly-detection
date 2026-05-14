import httpx
from fastapi import APIRouter, Depends
from ..dependecies import get_shared_client
from ..services.fintraffic import all_stations

router= APIRouter(tags=["stations"], responses={404:{"description":"not found :<"}})

@router.get("/stations")
async def allstations(client: httpx.AsyncClient = Depends(get_shared_client)):
    return await all_stations(client)




