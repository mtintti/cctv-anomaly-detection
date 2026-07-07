import PIL
from pydantic import BaseModel


class FoundOnnxObject(BaseModel):
    index: int
    x: float
    y: float
    w: float
    h: float
    confidence_score: float
    class_id: int
    class_name: str
    original_image_w: int
    original_image_h: int
    scale: float
    pad: tuple