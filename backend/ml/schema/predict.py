from pydantic import BaseModel, AnyUrl
from fastapi import UploadFile, File, Form


class predictBase(BaseModel):
    #file: list[UploadFile]
    #url: list[str] #a list of string for now, should be AnyURL in the future?
    file: UploadFile = File(default=[]),
    url: list[str] = Form(default=[])
