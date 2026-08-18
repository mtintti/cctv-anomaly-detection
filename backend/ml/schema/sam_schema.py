from pydantic import BaseModel


class SamRequest(BaseModel):
    bboxes_and_images: list  # or a properly typed model matching your rect shape


class MetricsSam(BaseModel):
    speed: dict

class samItems(BaseModel):
    finished_segmask: str | None
    sam_metrics: MetricsSam

class samResponse(BaseModel):
    image_name: str
    annotations: dict | None
    sam_items: list[samItems]