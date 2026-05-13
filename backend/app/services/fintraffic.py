import httpx
from fastapi import HTTPException

DIGITRAFFIC_BASE = "https://tie.digitraffic.fi/api/weathercam/v1/"

# Shared client — created once, reused across requests (efficient, not per-request)
_client: httpx.AsyncClient | None = None

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=DIGITRAFFIC_BASE,
            timeout=httpx.Timeout(10.0, connect=5.0),
            headers={"Accept": "application/json"},
        )
    return _client

async def camera_station(camera_id: str) -> dict:
    client = await get_client()
    try:
        response = await client.get(f"/stations/{camera_id}")
        response.raise_for_status()   # raises on 4xx/5xx
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Digitraffic API timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")
        raise HTTPException(status_code=502, detail="Digitraffic API error")

async def all_stations():
    client = await get_client()
    try:
        response = await client.get(f"/stations")
        print("\n in fintraffic all stations api call, res: ")
        print(response)
        response.raise_for_status()   # raises on 4xx/5xx
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Digitraffic API timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Stations not found")
        raise HTTPException(status_code=502, detail="Digitraffic API error")