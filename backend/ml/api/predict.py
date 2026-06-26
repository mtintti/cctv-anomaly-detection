import time
import urllib.request
import numpy as np
import onnxruntime
import requests
from PIL import Image
from io import BytesIO
from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from backend.app.config import logger
from backend.ml.schema.predict import predictBase


router = APIRouter()
sess = onnxruntime.InferenceSession(
    'C:/ohjelmointi/HobbyProjects/cctv-anomaly-detection/runs/segment/model_v9/weights/best.onnx')

allowed_types = {'image/jpeg', 'image/png', 'application/pdf', 'text/plain', 'JPEG', 'PNG'}
max_size_allowed = 1024 * 1024 *25 #24mb

ml_inference_log = []

async def filecheck(f, req, size = None):
    file_size = 0
    #print("filecheck ", f)
    if hasattr(f, "content_type"):  #content_type or f.format not in allowed_types:
        if f.content_type not in allowed_types:
            #print("file content type, ", f.content_type)
            raise HTTPException(status_code=415, detail='wrong type of file, use .png, .jpg or .pdf')
        else:
            #print("file is in allowed format/type ")
            file_size += int(req.headers.get("content-length"))
            #print(file_size)
    else:
        if f not in allowed_types:
            #print("res.headers[Content-Type]", f)
            raise HTTPException(status_code=415, detail='wrong type of file, use .png, .jpg or .pdf')
        if f in allowed_types:
            file_size += int(size)
            #print("file is in allowed format/type ")
            #print(file_size)

    '''elif hasattr(f, "format"):
        if f.format not in allowed_types:
            print("file.format", f.format)
            raise HTTPException(status_code=415, detail='wrong type of file, use .png, .jpg or .pdf')'''



    #print(f"{file_size/ 1024 / 1024} MB and max filesize {max_size_allowed / 1024 / 1024} MB")
    if file_size > max_size_allowed:
        raise HTTPException(status_code=413,
                            detail=f"File too large. Limit is {max_size_allowed / 1024 / 1024} MB.")

    return f

async def url_change_to_img(invi_url,indx_for_url, req):
    #url_img_name = f"backend/ml/processed/invifile{indx_for_url}.jpg"
    #print("invi url_change_to for ", invi_url)
    # old res = urllib.request.urlretrieve(invi_url, url_img_name)
    # no longer adding images to disk ^

    res = requests.get(invi_url, stream=True)
    checked_img = await filecheck(res.headers["Content-Type"], req, res.headers["Content-Length"])
    bytes_from_checkedimg = res.content

    #past code when we stored url images to disk in backend/processed
    # img = Image.open(url_img_name)
    #checked_img = await filecheck(res.headers, req)
    #print("checked image is a ",type(checked_img))
    #buff = BytesIO()
    #checked_img.save(buff, 'JPEG')
    #bytes_from_checkedimg = buff.getvalue()
    #print(type(bytes_from_checkedimg), " changed to be rgb and saved as a jpeg. returning bytes :? ... ")

    return bytes_from_checkedimg

async def image_process(bytes_from_img):
    try:
        #print("\n what got in image_proccess", bytes_from_img)
        #print("type of?? ", type(bytes_from_img))
        #test_image = cv2.imread(str_got)
        start = time.perf_counter()
        image_stream = BytesIO(bytes_from_img)
        #print("then img_stream type of?? ", type(image_stream))
        test_image = Image.open(image_stream).convert("RGB")
        test_image.load()
        w, h = test_image.size

        #pienennetään img kokoa koska model expectaa 512x512 kokoisen kuvan,
        # w ja h tarvitaan jotta img voidaan resizeta oikeaan alkuperäiseen muotoon
        nw = 512
        nh = int(h * (nw / w))
        resized_img= test_image.resize((nw, nh), Image.BICUBIC)

        changed = np.array(resized_img, dtype=np.float32)
        changed = changed / 255.0
        changed = np.transpose(changed, (2,0,1))
        changed = np.expand_dims(changed, axis=0)

        ml_inference_log.append((time.perf_counter() - start) * 1000)
        return changed, w,h
    except Exception:
        logger.error("error in image_proccess, /predict: ", exc_info=True)


def get_predictions(data, w, h):
    start = time.perf_counter()

    input = sess.get_inputs()[0].name
    #print("\n \pred get predictions, in", input)
    #print("\n input dtype ", sess.get_inputs()[0].type)
    #print("\n data in .onnx model, ", type(data))
    out_all = [output_invi.name for output_invi in sess.get_outputs()]
    #print("output, ", out_all)
    start_sess = time.perf_counter()
    res = sess.run(out_all,  {'images':data})
    #print(f"session's Inference time: {(time.perf_counter() - start_sess) * 1000:.2f} ms")
    ml_inference_log.append((time.perf_counter() - start_sess) * 1000)
    #print("\n res of get onnx, ", type(res))
    #print(res)
    return res



@router.post("/predict")
async def get_prediction(req: Request, file: list[UploadFile] = File(default=[]), url: list[str] = Form(default=[])): #file: UploadFile = File(...),
    try:

        print("files received:", [f.filename for f in file])
        print("urls received:", url)
        indx_for_url = 0
        print("cleared? ml_log ", len(ml_inference_log))

        start_wholerun = time.perf_counter()

        if len(file) > 0:
            #file handling
            for f in file:
                start_handleimg = time.perf_counter()
                filebool = await filecheck(f, req)
                bytes_from_img = await filebool.read()
                ml_inference_log.append((time.perf_counter() - start_handleimg) * 1000)
                reswith_width_height = await image_process(bytes_from_img)
                res = reswith_width_height[0]
                w = reswith_width_height[1]
                h = reswith_width_height[2]

                get_predictions(res, w, h)


        if len(url) > 0:
            #changing url to a bytes, bytes -> to prediction to .onnx model
            for invi_url in url:
                indx_for_url += 1
                #print("for url file", invi_url)
                start_handleimg = time.perf_counter()
                bytes_from_url_img = await url_change_to_img(invi_url, indx_for_url,req)
                ml_inference_log.append((time.perf_counter() - start_handleimg) * 1000)
                res_url_WidthHeight = await image_process(bytes_from_url_img)
                res = res_url_WidthHeight[0]
                w = res_url_WidthHeight[1]
                h = res_url_WidthHeight[2]
                get_predictions(res, w, h)

        ml_inference_log.append((time.perf_counter() - start_wholerun) * 1000)

        sentence = ["file/img handling(filecheck&file.read()/url-to-img)","img preprocess time", "onnx session's Inference time", "results decode-to-img time"]
        for z, value in enumerate(ml_inference_log[:-1]):
            print(f"{sentence[z % 4]} {value:.2f} ms")
            #print(f"{value:.2f} ms")

        print("--- fin ---")
        print(f"Whole run's time {ml_inference_log[-1]:.2f} ms")
        print("")
        print("size ml_log ", len(ml_inference_log))
        ml_inference_log.clear()
        print("cleared ml_log ", len(ml_inference_log))

    except Exception:
        logger.error("error in /predict: ", exc_info=True)

