from PIL.Image import Image
from pydantic import BaseModel, field_serializer


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

    @field_serializer('original_img', when_used='json-unless-none')
    def lyhenna_tuloste(self, v: str) -> str:
        if len(v) > 30:
            return f"{v[:30]}...{v[-30:]}"
        return v
