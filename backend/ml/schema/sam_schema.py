from pydantic import BaseModel


class SamRequest(BaseModel):
    bboxes_and_images: list  # or a properly typed model matching your rect shape


class MetricsSam(BaseModel):
    speed: dict

class samItems(BaseModel):
    finished_segmask: str | None
    finished_training_img: str | None
    sam_metrics: MetricsSam

class samResponse(BaseModel):
    image_name: str
    belongs_to_rect: str
    annotations: str | None
    sam_items: list[samItems]