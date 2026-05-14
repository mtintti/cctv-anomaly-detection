import httpx

from . import settings
from pydantic import BaseModel, AnyUrl
from typing import Optional

# client on saatavilla globalisti moneen saman hostin api requestiin, clientti tehdään vain kerran
# host on laitettuna settings obj (Settings()) /config.py tiedostosta joka saa tiedot .env
# kun appi sammutetaan (lifestate = yield) -> client nollataan
_client:httpx.AsyncClient
async def shared_client_start():
    global _client

    _client = httpx.AsyncClient(
        base_url=settings.digitraffic_base,
        timeout=httpx.Timeout(10.0, connect=5.0),
        headers={"Accept": "application/json"},
    )
    print("\n ..dependencies done: ", _client)
    return _client



async def shared_client_close() -> None:
    global _client
    await _client.aclose()
    _client = None

def get_shared_client() -> httpx.AsyncClient:
    return _client


# pedantic data validointi REST API kutsuille, kun api requesti tapahtuu pedantic:illa
# saadaan vain halutut arvot apista. Pääkutsut jota käytetään json datan alkuun tapahtuvat MainObj luokalla
# MainObj luokassa päästään omiin nested object kutsuihin rajaamaan Mainobject:in alempia json responceja (esim. CameraMainObject { id: string, geometry (CameraCoord): { coordinates: [xxx.xxx.xxx] })

class CameraCoord(BaseModel):
    coordinates: tuple[float, float, float]

# kameran id url osoite kuviin, käytetään datasetissä ML modeliin
class CameraPresetsImg(BaseModel):
    id: str
    presentationName: str
    resolution: str
    imageUrl: AnyUrl

# properties json kutsussa, saadaan lähimmät kamerat ja Properties sisältää nested_object Presets -> url kuviin
class CameraProp(BaseModel):
    id: str
    name: str
    nearestWeatherStationId: int
    municipality: str
    presets: list[CameraPresetsImg]

# jos tiedetään ennestään validi json structuuri, voidaan suoraan asettaa <nimi_json> : class_structuuri_nimi
# eikä <json_nimi> : list[class_structuuri_nimi]
class CameraObjMain(BaseModel):
    id: str
    geometry: CameraCoord
    properties: CameraProp
    #presets: list[dict[CameraPresetsImg]]


class StationPresets(BaseModel):
    id: str

class StationProp(BaseModel):
    id: str
    name: str
    dataUpdatedTime: str
    presets: list[StationPresets]

class StationFeat(BaseModel):
    type: str
    id: str
    geometry: CameraCoord # sama coord nimitys ja tuple data struct, CameraCoord voidaan käyttää uudestaan
    properties: StationProp

class StationObjMain(BaseModel):
    features: list[StationFeat]