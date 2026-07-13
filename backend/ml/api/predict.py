import base64
import time

import numpy as np
import onnxruntime
import requests
import starlette.datastructures
from PIL import Image
from io import BytesIO
import torch
import torchvision.ops as ops
from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from requests import Session

from backend.app.config import logger, loggercrier
from backend.ml.api.letterboxing import letterbox, ImgSize
from backend.ml.api.onnxtoimg import onnx_to_img #objects_found was previously here, objects_found
from backend.ml.schema.json_response import JsonResponse, Inviprediction, Predictiondetails

router = APIRouter()
sess = onnxruntime.InferenceSession(
    'C:/ohjelmointi/HobbyProjects/cctv-anomaly-detection/runs/segment/model_v9/weights/best.onnx')

allowed_types = {'image/jpeg', 'image/png', 'application/pdf', 'text/plain', 'JPEG', 'PNG'}
max_size_allowed = 1024 * 1024 *25 #24mb

ml_inference_log = []
#objects_found = []
async def filecheck(f, req, size = None):
    file_size = 0
    if hasattr(f, "content_type"):  #content_type or f.format not in allowed_types:
        if f.content_type not in allowed_types:
            raise HTTPException(status_code=415, detail='wrong type of file, use .png, .jpg or .pdf')
        else:
            file_size += int(req.headers.get("content-length"))
    else:
        if f not in allowed_types:
            raise HTTPException(status_code=415, detail='wrong type of file, use .png, .jpg or .pdf')
        if f in allowed_types:
            file_size += int(size)


    #print(f"{file_size/ 1024 / 1024} MB and max filesize {max_size_allowed / 1024 / 1024} MB")
    if file_size > max_size_allowed:
        raise HTTPException(status_code=413,
                            detail=f"File too large. Limit is {max_size_allowed / 1024 / 1024} MB.")

    return f

async def url_change_to_img(invi_url,indx_for_url, req, s):
    '''if indx_for_url != len(url):
        print("invi_url ", invi_url)
        print("index_for ", indx_for_url, ", url length: ", len(url))
        all_urls.append(invi_url)
        print("length of all_urls ", len(all_urls))
        bytes_from_img = None
        return bytes_from_img

    if indx_for_url == len(url):
        all_urls.append(invi_url)
        print("length of all_urls ", len(all_urls))
        for u in all_urls:'''

    res = s.get(invi_url, timeout=10)
    #res = requests.get(invi_url, stream=True, timeout=10)
    checked_img = await filecheck(res.headers["Content-Type"], req, res.headers["Content-Length"])
    bytes_from_checkedimg = res.content
    return bytes_from_checkedimg




async def image_process(bytes_from_img):
    # resizing original image size to onnx models expected/trained on input size of 512x512. we then change the 512x512 image to expected onnx models input.
    # we return onnx model input, original image in PIL form, original images width, original images h
    try:
        start = time.perf_counter()
        image_stream = BytesIO(bytes_from_img)
        test_image = Image.open(image_stream).convert("RGB")
        test_image.load()

        original_img_w, original_img_h = test_image.size
        img_arr = np.array(test_image)
        letterbox_res = letterbox(img_arr, ImgSize(512, 512))
        resized_img = letterbox_res[0]
        scale = letterbox_res[1]
        pad = letterbox_res[2]

        #pienennetään img kokoa koska model expectaa 512x512 kokoisen kuvan,
        # w ja h tarvitaan jotta img voidaan resizeta oikeaan alkuperäiseen muotoon
        nw = 512
        nh = int(original_img_h * (nw / original_img_w))

        changed = np.array(resized_img, dtype=np.float32)
        changed = changed / 255.0
        changed = np.transpose(changed, (2,0,1))
        changed = np.expand_dims(changed, axis=0)

        ml_inference_log.append((time.perf_counter() - start) * 1000)
        return changed, test_image, original_img_w, original_img_h, scale, pad
    except Exception:
        logger.expection("error in image_proccess, /predict: ", exc_info=True)



def get_predictions(data, original_image, original_img_w, original_img_h, scale, pad, objects_found):
    global classname_id
    start = time.perf_counter()

    input = sess.get_inputs()[0].name
    out_all = [output_invi.name for output_invi in sess.get_outputs()]
    start_sess = time.perf_counter()
    res = sess.run(out_all,  {'images':data})
    ml_inference_log.append((time.perf_counter() - start_sess) * 1000)
    start_decodeimg = time.perf_counter()
    output0 = res[0]
    output1 = res[1]

    output0 = output0[0]
    output1 = output1[0]

    scores = output0[0:300, 4]
    out0 = torch.from_numpy(output0)
    prediction_scores = torch.from_numpy(scores)
    reduced_output_indx = ops.nms(out0[:,0:4],prediction_scores,0.60)
    index_lookup = reduced_output_indx.tolist()
    pruned_output0 = []
    index = 0


    for x in range(len(output0)):
        if index_lookup[index] is x :
            pruned_output0.append(output0[x])
            index += 1

    out0arr = np.array(pruned_output0)

    boxes = out0arr[:,0:6] # was [:,0:9]
    coeffincies_segmasks = out0arr[:,6:] #was output0[:,9:]
    segmasks_prototypes = output1

    #overlay_seg, overlay_bbox, blended_together, original_image_RGBA = onnx_to_img(boxes, coeffincies_segmasks, segmasks_prototypes, original_img_w, original_img_h, original_image, scale, pad)
    final_composed_images, original_image_to_use = onnx_to_img(boxes, coeffincies_segmasks, segmasks_prototypes, original_img_w, original_img_h, original_image, scale, pad, objects_found)
    ml_inference_log.append((time.perf_counter() - start_decodeimg) * 1000)
    return final_composed_images, original_image_to_use



@router.post("/predict")
async def get_prediction(req: Request, file: list[UploadFile] = File(default=[]), url: list[str] = Form(default=[])): #file: UploadFile = File(...),
    try:

        toprocess = []
        json_response_all = []
        print("files received:", [f.filename for f in file])
        print("urls received:", url)
        indx_for_url = 0
        print("cleared? ml_log ", len(ml_inference_log), " toprocess ", len(toprocess)) #" objects_found ", len(objects_found), "
        belongto_name = "name"

        for u in url:
            toprocess.append(u)
            print("adding ", u , " ", len(toprocess))
        for f in file:
            toprocess.append(f)
            print("adding ", f, " ", len(toprocess))

        logger.info("final toprocess length", len(toprocess))
        s = requests.Session()

        start_wholerun = time.perf_counter()
        for item in toprocess:
            objects_found = []
            start_handleimg = time.perf_counter()
            if type(item) == starlette.datastructures.UploadFile:
                belongto_name = item.filename
                filebool = await filecheck(item, req)
                bytes_from_img = await filebool.read()
            elif type(item) == str:
                    belongto_name = item
                    indx_for_url += 1
                    bytes_from_img = await url_change_to_img(item, indx_for_url, req, s)
            else:
                # file is not processable, as it is not a file or a url
                logger.info("to_process is not a file or a url. from main_prediction_loop ", exc_info=True)

            timefromstart_handleimg = (time.perf_counter() - start_handleimg) * 1000
            appendable_handleimg = (timefromstart_handleimg, item)
            ml_inference_log.append(appendable_handleimg)

            reswith_width_height = await image_process(bytes_from_img)
            res = reswith_width_height[0]
            original_image = reswith_width_height[1]
            original_img_w = reswith_width_height[2]
            original_img_h = reswith_width_height[3]
            scale = reswith_width_height[4]
            pad = reswith_width_height[5]
            final_composed_images, original_image_to_use = get_predictions(res, original_image, original_img_w,
                                                                             original_img_h, scale, pad, objects_found)

            logger.info("final_composed_images length ", len(final_composed_images))
            start_encode = time.perf_counter()
            orig = original_image_to_use
            bufferorig = BytesIO()
            orig.save(bufferorig, format="PNG")
            origBytes = bufferorig.getvalue()
            encoded_orig = base64.b64encode(origBytes)
            final_bytes_to_resOrig = b'data:image/png;base64,' + encoded_orig
            for z in range(len(final_composed_images)):
                invidual = final_composed_images[z]
                index = invidual.index
                if(invidual.overlay_seg != None):
                    segmask = invidual.overlay_seg
                    buffer = BytesIO()
                    segmask.save(buffer, format="PNG")
                    segmaskBytes = buffer.getvalue()
                    encoded_seg = base64.b64encode(segmaskBytes)
                    final_bytes_to_resSeg = b'data:image/png;base64,' + encoded_seg

                    bbox = invidual.overlay_bbox
                    bufferbbox = BytesIO()
                    bbox.save(bufferbbox, format="PNG")
                    bboxBytes = bufferbbox.getvalue()
                    encoded_bbox = base64.b64encode(bboxBytes)
                    final_bytes_to_resBbox = b'data:image/png;base64,' + encoded_bbox

                    confidencescore = objects_found[z].confidence_score
                    class_id = objects_found[z].class_id
                    class_name = objects_found[z].class_name
                    predictions = Inviprediction(imageBbox=final_bytes_to_resBbox,imageSeg=final_bytes_to_resSeg)
                    details = Predictiondetails(class_id=class_id, class_name=class_name,confidence_score=confidencescore)
                    constructed = JsonResponse(belongsto=belongto_name, original_img=final_bytes_to_resOrig, details=[details], prediction=[predictions])  #{'imageBbox':bboxBytes}, {imageSeg:segmaskBytes}
                    json_response_all.append(constructed)


                else:
                    logger.info("skipped showing, results were none")
                    predictions = Inviprediction(imageBbox=None, imageSeg=None)
                    details = Predictiondetails(class_id=None, class_name=None, confidence_score=None)
                    constructed = JsonResponse(belongsto=belongto_name, original_img=final_bytes_to_resOrig,details=[details], prediction=[predictions])  # {'imageBbox':bboxBytes}, {imageSeg:segmaskBytes}
                    json_response_all.append(constructed)

            timefromstart_encode = (time.perf_counter() - start_encode) * 1000
            appendable_encode = (timefromstart_encode, item)
            ml_inference_log.append(appendable_encode)

        #final metrics after all images are shown
        ml_inference_log.append((time.perf_counter() - start_wholerun) * 1000)

        sentence = ["file/img handling(filecheck&file.read()/url-to-img)", "img preprocess to tensor",
                                    "onnx session's Inference time", "results made to bbox and segmask", "encodeded to response for <img> tag"]
        for z, value in enumerate(ml_inference_log[:-1]):
            if type(value) == tuple:
                print(f"{sentence[z % 5]} {value[0]:.2f} ms for item " , value[1])
            else:
                print(f"{sentence[z % 5]} {value:.2f} ms")

        print("--- fin ---")
        print(f"Whole run's time {ml_inference_log[-1]:.2f} ms")
        print("all responses ", len(json_response_all))
        print("internal data, and debug: size ml_log ", len(ml_inference_log), " objects_found ", len(objects_found))
        print("")
        ml_inference_log.clear()
        objects_found.clear()
        toprocess.clear()
        json_response_all.clear()
        print("cleared ml_log ", len(ml_inference_log), " objects_found ", len(objects_found), " toprocess ",
                    len(toprocess), " all resposes ", len(json_response_all))

    except Exception:
        loggercrier.error("error in /predict: ", exc_info=True)
