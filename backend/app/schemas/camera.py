from typing import Optional

from pydantic import BaseModel, AnyUrl

# pedantic data validointi REST API kutsuille, kun api requesti tapahtuu pedantic:illa
# saadaan vain halutut arvot apista. Pääkutsut jota käytetään json datan alkuun tapahtuvat MainObj luokalla
# MainObj luokassa päästään omiin nested object kutsuihin rajaamaan Mainobject:in alempia json responceja (esim. CameraMainObject { id: string, geometry (CameraCoord): { coordinates: [xxx.xxx.xxx] })

class CameraCoord(BaseModel):
    coordinates: tuple[float, float, float]

# kameran id url osoite kuviin, käytetään datasetissä ML modeliin
class CameraPresetsImg(BaseModel):
    id: str
    presentationName: Optional[str] = None
    resolution: str
    imageUrl: str #was AnyUrl, but datatype conversion error in pycopg

# properties json kutsussa, saadaan lähimmät kamerat ja Properties sisältää nested_object Presets -> url kuviin
class CameraProp(BaseModel):
    id: str
    name: str
    nearestWeatherStationId: Optional[int] = None
    municipality: str
    presets: list[CameraPresetsImg]

# jos tiedetään ennestään validi json structuuri, voidaan suoraan asettaa <nimi_json> : class_structuuri_nimi
# eikä <json_nimi> : list[class_structuuri_nimi]
class CameraObjMain(BaseModel):
    id: str
    geometry: CameraCoord
    properties: CameraProp
    #presets: list[dict[CameraPresetsImg]]

