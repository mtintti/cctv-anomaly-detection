import uuid
from pydantic import BaseModel


class Locust_to_postgres(BaseModel):
    job_id: int
    jobs_predict_id: str
    class_id: int
    confidence_score: str
    image_file_handling: str
    preprocess_to_tensor: str
    inference: str
    bbox_and_segmask: str
    original_img_encode: str
    batchlist_creation: str
    encode_images: str
    redis: str
    whole_runs_time: str