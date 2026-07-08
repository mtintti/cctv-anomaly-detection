import time

import numpy as np
import onnxruntime
import requests
from PIL import Image
from io import BytesIO
import torch
import torchvision.ops as ops
from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException

from backend.app.config import logger
from backend.ml.api.letterboxing import letterbox, ImgSize
from backend.ml.api.onnxtoimg import onnx_to_img #objects_found was previously here, objects_found


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

async def url_change_to_img(invi_url,indx_for_url, req):

    res = requests.get(invi_url, stream=True)
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
    final_composed_images, original_image_RGBA = onnx_to_img(boxes, coeffincies_segmasks, segmasks_prototypes, original_img_w, original_img_h, original_image, scale, pad, objects_found)
    ml_inference_log.append((time.perf_counter() - start_decodeimg) * 1000)
    return final_composed_images, original_image_RGBA



@router.post("/predict")
async def get_prediction(req: Request, file: list[UploadFile] = File(default=[]), url: list[str] = Form(default=[])): #file: UploadFile = File(...),
    try:
        '''
        #objects_found = [] was here, but our objects_found index list would persist if there would be an file and images passed through the api, aka
        file one and one imageurl is passed to api
        our we process the one file first and fine 4 different anomalies in it, 
        File log:
            finalised boxes and coeffs shape  (4, 6)   (4, 32)
            in range objects_found  index=0 
            in range objects_found  index=1
            in range objects_found  index=2
            in range objects_found  index=3
            moving to reshape_combined 
            shape of masks_sigmid  torch.Size([4, 128, 128])
            
            
            moved past combining both overlays
            final_composed length,  4
            length of all_colors  4
        # we then pass and show the 4 images in our predict main loop. We then process our image and pass it to our onnx model session.
        # our objects found never gets cleared in between our file and image processing. the lists past additions are present still
        Image Log:
            info appended to objects found  5
            past loop boxes in onnx_to_img  5
            finalised boxes and coeffs shape  (1, 6)   (1, 32)
            in range objects_found  index=0 
            in range objects_found  index=1
            in range objects_found  index=2
            in range objects_found  index=3
            in range objects_found  index=0 # new images prediction, 0 -> 3 are files
            shape of bbox coords  torch.Size([5, 4]) # 4 files bbox coords and one images :<
        
        
        '''
        objects_found = []
        print("files received:", [f.filename for f in file])
        print("urls received:", url)
        indx_for_url = 0
        print("cleared? ml_log ", len(ml_inference_log), " objects_found ", len(objects_found))

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
                original_image = reswith_width_height[1]
                original_img_w = reswith_width_height[2]
                original_img_h = reswith_width_height[3]
                scale = reswith_width_height[4]
                pad = reswith_width_height[5]
                #overlay_seg, overlay_bbox, blended_together, original_image_RGBA = get_predictions(res, original_image, original_img_w, original_img_h, scale, pad)
                final_composed_images, original_image_RGBA = get_predictions(res,original_image, original_img_w, original_img_h, scale, pad, objects_found)
                for z in range(len(final_composed_images)):
                    invidual = final_composed_images[z]
                    index = invidual.index
                    segmask = invidual.overlay_seg
                    bbox = invidual.overlay_bbox
                    blended_together = invidual.blended_together
                    complete = Image.alpha_composite(original_image_RGBA, blended_together)
                    complete.show()


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
                original_image = res_url_WidthHeight[1]
                original_img_w = res_url_WidthHeight[2]
                original_img_h = res_url_WidthHeight[3]
                scale = res_url_WidthHeight[4]
                pad = res_url_WidthHeight[5]
                #overlay_seg, overlay_bbox, blended_together, original_image_RGBA = get_predictions(res,original_image, original_img_w, original_img_h, scale, pad)
                final_composed_images, original_image_RGBA = get_predictions(res,original_image, original_img_w, original_img_h, scale, pad, objects_found)
                for z in range(len(final_composed_images)):
                    invidual = final_composed_images[z]
                    index = invidual.index
                    segmask = invidual.overlay_seg
                    bbox = invidual.overlay_bbox
                    blended_together = invidual.blended_together
                    complete = Image.alpha_composite(original_image_RGBA, blended_together)
                    complete.show()

        ml_inference_log.append((time.perf_counter() - start_wholerun) * 1000)

        sentence = ["file/img handling(filecheck&file.read()/url-to-img)","img preprocess time", "onnx session's Inference time", "results decode-to-img time"]
        for z, value in enumerate(ml_inference_log[:-1]):
            print(f"{sentence[z % 4]} {value:.2f} ms")
            #print(f"{value:.2f} ms")

        print("--- fin ---")
        print(f"Whole run's time {ml_inference_log[-1]:.2f} ms")
        print("")
        print("found objects")
        for x in objects_found:
            print(x)
        print("size ml_log ", len(ml_inference_log),  " objects_found ", len(objects_found))
        ml_inference_log.clear()
        objects_found.clear()
        print("cleared ml_log ", len(ml_inference_log),  " objects_found ", len(objects_found))

    except Exception:
        logger.error("error in /predict: ", exc_info=True)

