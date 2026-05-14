import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError

from ..dependecies import CameraObjMain, StationObjMain

# itse REST API kutsut. clientistä saadaan api base + haluttu endpoint.
# saatu response Data validoidaan/parsataan vain tarvittaviin arvoihin (parts_needed),
# käyttämällä Pedantic MainObj:tia, ja mahdollisia nested_object:teja.

async def camera_station(camera_id: str, client:httpx.AsyncClient):
    try:
        response = await client.get(f"/stations/{camera_id}")
        response.raise_for_status()   # raises on 4xx/5xx
        #return response.json()
        try:
            partNeeded = CameraObjMain.model_validate(response.json())
            print(partNeeded)
            print(" ")
            if ValidationError:
                print(ValueError)
            return partNeeded
        except ValidationError as er:
            print(er)

    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Digitraffic API timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Camera {camera_id} not found")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Digitraffic API error")

async def all_stations(client: httpx.AsyncClient):
    #client = await get_client()

    try:
        response = await client.get(f"/stations")
        print("\n in fintraffic all stations api call, res: ")
        print(response)
        response.raise_for_status()   # raises on 4xx/5xx
        #return response.json()
        try:
            partNeeded = StationObjMain.model_validate(response.json())
            print(partNeeded)
            print(" ")
            if ValidationError:
                print(ValueError)
            return partNeeded
        except ValidationError as er:
            print(er)
    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Digitraffic API timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stations not found")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Digitraffic API error")