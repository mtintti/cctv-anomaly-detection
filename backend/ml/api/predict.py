
import urllib.request
from typing import Any

import cv2
import httpx
import numpy as np
from cv2 import Mat
from fastapi.routing import APIRouter
from fastapi import Depends, File, UploadFile, Request, HTTPException
import onnxruntime
from PIL import Image
from io import BytesIO

from numpy import ndarray, dtype
from starlette.responses import Response

from backend.app.config import logger

urls = ['C:/ohjelmointi/HobbyProjects/cctv-training/images/train/C0150409_tie-2-karkkila.jpg', ]

router = APIRouter()
sess = onnxruntime.InferenceSession(
    'C:/ohjelmointi/HobbyProjects/cctv-anomaly-detection/runs/segment/model_v9/weights/best.onnx')

allowed_types = {'image/jpeg', 'image/png', 'application/pdf', 'text/plain'}
max_size_allowed = 1024 * 1024 *25 #24mb
def url_change_to_img(url):
    res = urllib.request.urlopen(url)
    image_arr = np.asarray(bytearray(res.read()), dtype="uint8")
    image_cv = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
    return image_cv

def image_process(str_got): #file)-> ndarray | Image.Image | str
    #print("img_process in file", file.headers.)
    try:
        print("\n string got in image_proccess", str_got)
        test_image = cv2.imread(str_got)
        print("test, ", test_image.size)
        '''test_image = Image.open(BytesIO(file))
        print("testimg size ", test_image.size, " img format ", test_image.format)
        test_image.show()
        test_image.save(test_image, 'JPG')'''
        #print("testimg size ", test_image.size, " img data ", test_image.data)
        #image_arr = np.asarray(bytearray(test_image.read()), dtype="uint8")
        #image_cv = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
        #return image_cv
        return test_image
    except Exception:
        logger.error("error in image_proccess, /predict: ", exc_info=True)


def get_predictions(data):
    input = sess.get_inputs()[0].name
    print("\n \pred get predictions, ", input)
    print("\n data got to def, ", data)
    out = sess.get_outputs()
    res = sess.run(out,{'images':data})
    print("\n res of get onnx, ", res)
    return res

'''@router.get("/predict")
async def get_file(req: Request):
    res = "image_name.jpg"
    return res
'''

@router.post("/predict")
async def get_prediction(req: Request,file: UploadFile = File(...)):
    try:
        print("file got as?? ", file)
        if file.content_type not in allowed_types:
            print("file content type, ", file.content_type)
            raise HTTPException(status_code=415, detail='wrong type of file, use .png, .jpg or .pdf')

        file_size = int(req.headers.get("content-length"))
        print(file_size)
        if file_size > max_size_allowed:
            raise HTTPException(status_code=413, detail=f"File too large. Limit is {max_size_allowed / 1024 / 1024} MB.")
        #return file.filename
        print("\n files type, ")
        print(file.content_type)
        print("\n file gotten in /predict")
        print(file.filename)
        #test_image = Image.open(BytesIO(file))
        ##return {"filename": file.filename, "filecontent": file.content_type, "filesize":file_size}
        #data = url_change_to_img(file)
        ##res = image_process()
        ##print("\n res got from image_proccess, " , res)
        ##response_onnx = get_predictions(res)
        ##print("\n onnx got back, ", response_onnx)
        return {"filename": file.filename} ##"onnx": response_onnx,
    except Exception:
        logger.error("error in /predict: ", exc_info=True)
    #data = image_process(file)


