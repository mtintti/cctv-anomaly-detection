import asyncio
import base64
import concurrent.futures
import time
from asyncio import as_completed
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from sys import exc_info
from typing import Tuple

import PIL.Image
import httpx
import numpy as np
import onnxruntime
import requests
import starlette.datastructures
from PIL import Image
from io import BytesIO
import torch
import torchvision.ops as ops
from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from pydantic import TypeAdapter

from backend.app.config import logger, loggercrier
from backend.ml.api.letterboxing import letterbox, ImgSize
from backend.ml.api.onnxtoimg import onnx_to_img #objects_found was previously here, objects_found
from backend.ml.schema.json_response import JsonResponse, Inviprediction, Predictiondetails

router = APIRouter()
sess = onnxruntime.InferenceSession(
    'backend/ml/best.onnx')

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

async def url_change_to_img(indx_for_url, req, url, client:httpx.AsyncClient, batchres):

    async def checkimg(res):
        checked_img = await filecheck(res.headers["Content-Type"], req, res.headers["Content-Length"])
        bytes_from_checkedimg = res.content
        return bytes_from_checkedimg


    if indx_for_url == 1:
        for u in url:
            #print("in async client loop for ", u)
            batchres.append(await client.get(u))

    bytes_from_checkedimg = await checkimg(batchres[indx_for_url -1])
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
        loggercrier.expection("error in image_proccess, /predict: ", exc_info=True)


async def get_predictions(data, original_image, original_img_w, original_img_h, scale, pad, objects_found):
    global classname_id

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
    #final_composed_images, original_image_to_use = onnx_to_img(boxes, coeffincies_segmasks, segmasks_prototypes, original_img_w, original_img_h, original_image, scale, pad, objects_found)
    final_composed_images, original_image_to_use = await onnx_to_img(boxes, coeffincies_segmasks, segmasks_prototypes, original_img_w, original_img_h, original_image, scale, pad, objects_found)
    ml_inference_log.append((time.perf_counter() - start_decodeimg) * 1000)
    return final_composed_images, original_image_to_use


async def batchlist_encode(belongto_name: str, objects_found: list, final_composed_images: list, item, batchlist, encoded_original_img):

        logger.info(("length of final_composed_images ", len(final_composed_images)))
        start_batchlist = time.perf_counter()
        #final_bytes_to_resOrig = encode_image(orig)

        for z in range(len(final_composed_images)):
            invidual = final_composed_images[z]
            if (invidual.overlay_seg != None):
                segmask = invidual.overlay_seg
                #final_bytes_to_resSeg = encode_image(segmask)

                bbox = invidual.overlay_bbox
                #final_bytes_to_resBbox = encode_image(bbox)

                confidencescore = objects_found[z].confidence_score
                class_id = objects_found[z].class_id
                class_name = objects_found[z].class_name

                predictions = Inviprediction(imageBbox=None, imageSeg=None)
                details = Predictiondetails(class_id=class_id, class_name=class_name,
                                                confidence_score=confidencescore)
                constructed = JsonResponse(belongsto=belongto_name, original_img=encoded_original_img,
                                               details=[details],
                                               prediction=[predictions])
                batchlist.append(((bbox), (segmask), constructed))
                #json_response_all.append(constructed)
                #logger.info(("length of batchlist ", len(batchlist)))

            else:
                logger.info("skipped showing, results were none")
                predictions = Inviprediction(imageBbox=None, imageSeg=None)
                details = Predictiondetails(class_id=None, class_name=None, confidence_score=None)
                constructed = JsonResponse(belongsto=belongto_name, original_img=encoded_original_img,
                                           details=[details],
                                           prediction=[predictions])  # {'imageBbox':bboxBytes}, {imageSeg:segmaskBytes}
                #json_response_all.append(constructed)
                batchlist.append(constructed)
            logger.debug(("length of batchlist ", len(batchlist)))

        timefromstart_batchlist = (time.perf_counter() - start_batchlist) * 1000
        ml_inference_log.append(timefromstart_batchlist)

def encode_image(image_tochange):
        buffer_touse = BytesIO()
        image_tochange.save(buffer_touse, format="PNG")
        changedto_Bytes = buffer_touse.getvalue()
        encoded_orig = base64.b64encode(changedto_Bytes)
        final_bytes_to_encoded_png = b'data:image/png;base64,' + encoded_orig
        return final_bytes_to_encoded_png

async def encodeimagetojson(batchlist, json_response_all, item: str | UploadFile):
    try:

        for l in batchlist:
                if type(l) == tuple:

                    final_bytes_to_resBbox, final_bytes_to_resSeg = await asyncio.gather(
                        asyncio.to_thread(encode_image, l[0]), asyncio.to_thread(encode_image, l[1]))

                    l[2].prediction[0].imageBbox = final_bytes_to_resBbox
                    l[2].prediction[0].imageSeg = final_bytes_to_resSeg


                    #print("new")
                    #print(l[2].prediction)
                    # details = Predictiondetails()
                    constructed = l[2]
                    json_response_all.append(constructed)

                else:
                    json_response_all.append(l)

                    # print("lenght of json ",len(json_response_all))
                    # batchlist.append(constructed)

        # logger.debug(("length of json_responce ", len(json_response_all)))

    except Exception:
        loggercrier("encoding image failed! ", exc_info=True)



@router.post("/predict")
async def get_prediction(req: Request, file: list[UploadFile] = File(default=[]), url: list[str] = Form(default=[])): #file: UploadFile = File(...),

    try:

        toprocess = []
        json_response_all = []
        batchres = []
        batchlist = []
        encode_list = []
        print("files received:", [f.filename for f in file])
        print("urls received:", url)
        indx_for_url = 0
        print("cleared? ml_log ", len(ml_inference_log), " toprocess ",
              len(toprocess))  # " objects_found ", len(objects_found), "
        belongto_name = "name"
        client = httpx.AsyncClient()

        for u in url:
            toprocess.append(u)
            print("adding ", u, " ", len(toprocess))
        for f in file:
            toprocess.append(f)
            print("adding ", f, " ", len(toprocess))

        logger.info(("final toprocess length", len(toprocess)))

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
                # async with httpx.AsyncClient() as client:
                bytes_from_img = await url_change_to_img(indx_for_url, req, url, client, batchres)
                # logger.info(("type of bytes from img ", type(bytes_from_img)))
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
            # final_composed_images, original_image_to_use = get_predictions(res, original_image, original_img_w,
            #                                                                 original_img_h, scale, pad, objects_found)
            final_composed_images, original_image_to_use = await get_predictions(res, original_image,
                                                                                   original_img_w, original_img_h,                                                              scale, pad, objects_found)
            # print(item_indx, len(toprocess))

             #JsonResponse.original_img = encoded
            #print(type(encoded))
            #print(encoded)
            start_originalencode = time.perf_counter()
            encoded = await asyncio.to_thread(encode_image, original_image_to_use)
            timefromstart_originalencode = (time.perf_counter() - start_originalencode) * 1000

            await batchlist_encode(belongto_name, objects_found, final_composed_images, item,
                                   batchlist, encoded)

        logger.info(("final batchlist length ", len(batchlist)))

        start_encode = time.perf_counter()
        await encodeimagetojson(batchlist, json_response_all, item)
        timefromstart_encode = (time.perf_counter() - start_encode) * 1000

        # final metrics after all images are shown
        ta = TypeAdapter(JsonResponse)
        # print(ta)
        # print(json_response_all[0])
        # res = ta.validate_python(json_response_all)
        # print(res)
        sendable = ta.dump_json(json_response_all)
        # print(sendable)
        ml_inference_log.append((time.perf_counter() - start_wholerun) * 1000)

        sentence = ["file/img handling(filecheck&file.read()/url-to-img)", "img preprocess to tensor",
                    "onnx session's Inference time", "results made to bbox and segmask"," once per det original image encode", "batchlisting items"]
        for z, value in enumerate(ml_inference_log[:-1]):
            if type(value) == tuple:
                print(f"{sentence[z % 6]} {value[0]:.2f} ms for item ", value[1])
            else:
                print(f"{sentence[z % 6]} {value:.2f} ms")
        print(f"encodeded to response for <img> tag {timefromstart_encode:.2f} ms")
        print("--- fin ---")
        print(f"Whole run's time {ml_inference_log[-1]:.2f} ms")
        print("all responses for final JSON ", len(json_response_all))
        print("internal lists, and debug: size ml_log ", len(ml_inference_log), " objects_found ", len(objects_found))
        print("")
        ml_inference_log.clear()
        objects_found.clear()
        toprocess.clear()
        json_response_all.clear()
        print("internal lists, cleared ml_log ", len(ml_inference_log), " objects_found ", len(objects_found),
              " toprocess ",
              len(toprocess), " all responses for final JSON ", len(json_response_all))
        return sendable

    except Exception:
        loggercrier.error("error in /predict: ", exc_info=True)

        #futures = processPool.map(task, [req], [file], [url], chunksize=4)
        '''response = loop.run_in_executor(processPool, task,req, file, url)
        print(type(response))
        print(response.)'''


