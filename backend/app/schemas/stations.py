from pydantic import BaseModel
from .camera import CameraCoord

# pedantic data validointi REST API kutsuille, kun api requesti tapahtuu pedantic:illa
# saadaan vain halutut arvot apista. Pääkutsut jota käytetään json datan alkuun tapahtuvat MainObj luokalla
# MainObj luokassa päästään omiin nested object kutsuihin rajaamaan Mainobject:in alempia json responceja (esim. CameraMainObject { id: string, geometry (CameraCoord): { coordinates: [xxx.xxx.xxx] })

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

class StationID(BaseModel):
    type: str
    id: str

class StationObjID(BaseModel):
    features: list[StationID]