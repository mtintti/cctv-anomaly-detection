from PIL.Image import Image
from pydantic import BaseModel

class Inviprediction(BaseModel):
    imageBbox: str | None
    imageSeg: str | None

class Predictiondetails(BaseModel):
    class_id: int | None
    class_name: str | None
    confidence_score: float | None

class JsonResponse(BaseModel):
    belongsto: str
    original_img: str
    details: list[Predictiondetails]
    prediction: list[Inviprediction]
