import uuid
from pydantic import BaseModel

class Inviprediction(BaseModel):
    imageBbox: str | None
    imageSeg: str | None

class Predictiondetails(BaseModel):
    class_id: int | None
    class_name: str | None
    confidence_score: float | None

class JsonResponse(BaseModel):
    belongsto: str | None
    original_img: str | None
    details: list[Predictiondetails]
    prediction: list[Inviprediction]

class PredictID(BaseModel):
    predict_id: uuid.UUID
    jsonresponse: list[JsonResponse]

