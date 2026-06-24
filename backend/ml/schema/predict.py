from fastapi import UploadFile
from pydantic import BaseModel, AnyUrl


class predictBase(BaseModel):
    file: list[UploadFile]
    url: list[str] #a list of string for now, should be AnyURL in the future?

