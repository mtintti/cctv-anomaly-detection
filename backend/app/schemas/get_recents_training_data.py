from datetime import datetime

from pydantic import BaseModel

class Recents_training_data(BaseModel):
    id: int
    image_name: str
    training_img: str
    updated_at: datetime
    annotations: list