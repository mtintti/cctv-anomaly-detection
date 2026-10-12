import datetime

from pydantic import BaseModel


class Datasets(BaseModel):
    user_id: int
    dataset_name: str
    images_number: list
    updated_at: datetime.datetime