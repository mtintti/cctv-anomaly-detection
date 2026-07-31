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
    img_w: int
    img_h: int
    details: list[Predictiondetails]
    prediction: list[Inviprediction]

class Metrics(BaseModel):
    handling: str | None
    preprocess_to_tensor: str | None
    inference: str | None
    bbox_and_segmask: str | None
    original_img_encode: str | None
    batchlist: str | None
    encode_img_tag: str | None
    redis: str | None
    whole_runs_time: str | None

class PredictID(BaseModel):
    predict_id: uuid.UUID
    jsonresponse: list[JsonResponse]
    metrics: list[Metrics]

