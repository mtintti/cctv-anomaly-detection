import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError
from ..schemas.camera import CameraObjMain
from ..schemas.stations import StationObjMain
from ..config import logger, loggercrier

# itse REST API kutsut. clientistä saadaan api base + haluttu endpoint.
# saatu response Data validoidaan/parsataan vain tarvittaviin arvoihin (parts_needed),
# käyttämällä Pedantic MainObj:tia, ja mahdollisia nested_object:teja.

async def camera_station(camera_id: str, client:httpx.AsyncClient):
    try:
        response = await client.get(f"/stations/{camera_id}")
        response.raise_for_status()   # raises on 4xx/5xx
        try:
            partNeeded = CameraObjMain.model_validate(response.json())
            logger.info("camera_id API call Pydantic validation happened, ", extra={"camera_id":camera_id})
            return partNeeded
        except ValidationError as er:
            loggercrier.error("API response Pedantic validation or parse ERROR", exc_info=True)

    except httpx.TimeoutException:
        loggercrier.error("Api response took too long timeout, check .log", exc_info=True)
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Digitraffic API timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            loggercrier.error("API was not found, check .log", exc_info=True)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Camera {camera_id} not found")
        loggercrier.error("Api response 502-gateway, check .log", exc_info=True)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Digitraffic API error")

async def all_stations(client: httpx.AsyncClient):
    try:
        response = await client.get(f"/stations")
        response.raise_for_status()   # raises on 4xx/5xx
        try:
            partNeeded = StationObjMain.model_validate(response.json())
            return partNeeded
        except ValidationError as er:
            loggercrier.error("API response Pedantic validation or parse ERROR", exc_info=True)
    except httpx.TimeoutException:
        loggercrier.error("Api response took too long, check .log", exc_info=True)
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Digitraffic API timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            loggercrier.error("API was not found, check .log", exc_info=True)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stations not found")
        loggercrier.error("Api response 502-gateway, check .log", exc_info=True)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Digitraffic API error")