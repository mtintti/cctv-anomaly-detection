import base64
import uuid

import numpy as np
import torch
import ultralytics
from fastapi import APIRouter
from PIL import Image
from io import BytesIO, StringIO
from pydantic import TypeAdapter
from starlette.responses import JSONResponse
from ultralytics.models.sam import Predictor as sam

from backend.app.config import logger
from backend.ml.schema.sam_schema import samResponse, samItems, SamRequest, MetricsSam
from backend.ml.api.letterboxing import letterbox, ImgSize
from backend.ml.api.predict import encode_image_in_batch

sam_router = APIRouter()


def scale_coordinates_canvas_to_img(x_cord, y_cord, bboxw, bboxh, canvas_width, canvas_height, original_img_w, original_img_h):
    ratio_w = original_img_w / canvas_width
    ratio_h = original_img_h / canvas_height

    x = x_cord * ratio_w
    y = y_cord * ratio_h
    x2 = bboxw * ratio_w
    y2 = bboxh * ratio_h
    return x, y, x2, y2

# muutetaan alkuperäisen muodon koordinaatit -> letterboxed tensor 512x512 muotoon
def scale_coordinates_img_to_tensor(x_cord, y_cord, bboxw, bboxh, scale, pad):
    pad_y = pad[0]
    pad_x = pad[1]

    x = x_cord * scale + pad_x
    y = y_cord * scale + pad_y

    x2 = bboxw * scale + pad_x
    y2 = bboxh * scale + pad_y

    p1tuple = (x, y)
    p2tuple = (x2, y2)
    return p1tuple, p2tuple

# muutetaan letterboxed koordinaatit sam segmentaatiosta -> alkuperäiseen muotoon
def rescale_segmask_coordinates(segmask, original_img_w, original_img_h):
    mask_in_tensor_form = torch.from_numpy(segmask)
    expected_shape = mask_in_tensor_form.unsqueeze(0)
    rescaled_mask = ultralytics.utils.ops.scale_masks(expected_shape[None].float(), (original_img_h, original_img_w))
    rescaled_mask = rescaled_mask.squeeze(0)  # removing the batch as our shape would be ( 1,N,W, H) otherwise
    rescaled_mask_only_w_h = rescaled_mask.squeeze(0)
    return rescaled_mask_only_w_h

# luodaan letterboxed yxz labels teksti tiedostoon joka tallennetaan käyttäjäkohtaiseen file managment sivuun
# käyttäjä ei itse näy tätä kuten luokkavärilliset segmentti maskit
def create_mask_yxz_labels(mask_Data, img_basename, classname, annotation_buffers: dict[str, StringIO]):

    try:

        normalized_coords = mask_Data.xyn
        if normalized_coords is None or all(len(p) == 0 for p in normalized_coords):
            return

        buffer = annotation_buffers.setdefault(img_basename, StringIO())

        for mask in normalized_coords:
            buffer.write("\n")
            buffer.write(str(classname))
            buffer.write(" ")
            for coord in np.nditer(mask):
                buffer.write(str(float(coord)))
                buffer.write(" ")

    finally:
        print("file done")

# käyttäjän näkemä segmentaatio maski alkuperäisen kuvan päällä, käytetään vain kuvakohtaiseen annonation.txt visuaalisointtin
def color_coded_overlay_SAMsegmask(mask, colorcoded_class):
    #mask = masks_Data.data[0].cpu().numpy()
    mask = (mask > 0.5).astype("uint8")

    overlay = np.zeros(
        (mask.shape[0], mask.shape[1], 4),
        dtype=np.uint8
    )
    overlay[mask == 1] = colorcoded_class
    seeing_sam = Image.fromarray(overlay)
    return seeing_sam
    #cv2.imwrite(str(outerpathdir / imgfilename), overlay)


@sam_router.post("/predict/{predict_id}/sam")
async def samInference(predict_id: uuid.UUID, payload: SamRequest):
    try:
        overrides = dict(conf=0.25, task="segment", imgsz=512, mode="predict", model="sam_b.pt")
        predictor = sam(overrides=overrides)

        annotation_buffers: dict[str, StringIO] = {}

        batchlist_sam_images = []
        response = []
        for curr in payload.bboxes_and_images:

            if curr.get('original_image'):
                string_to_bytes = curr.get('original_image')

                base64_img_bytes = string_to_bytes[22:].encode('utf-8')
                decoded_image_data = base64.decodebytes(base64_img_bytes)

                image_to_use = Image.open(BytesIO(decoded_image_data)).convert("RGB")
                image_to_use.load()

                original_img_w, original_img_h = image_to_use.size
                img_arr = np.array(image_to_use)
                letterbox_res = letterbox(img_arr, ImgSize(512, 512))
                resized_img = letterbox_res[0]
                scale = letterbox_res[1]
                pad = letterbox_res[2]
                print("type of resized_img ", type(resized_img))
                predictor.set_image(resized_img)

            else:

                if(curr.get('image_name')):
                    img_basename = curr.get('image_name')
                else:

                    classname = curr['classname']
                    colorcoded_class = curr['color']

                    min_x, min_y, max_x, max_y = scale_coordinates_canvas_to_img(
                        curr['left'], curr['top'], curr['left'] + curr['width'], curr['top'] + curr['height'],
                        curr['canvas_width'], curr['canvas_height'], original_img_w, original_img_h
                    )

                    p1tuple, p2tuple = scale_coordinates_img_to_tensor(min_x, min_y, max_x, max_y, scale, pad)
                    results = predictor(bboxes=[*p1tuple, *p2tuple], labels=classname)

                    for i, r in enumerate(results):
                        # color_coded luokkatiedot on eritelty erillisillä väreillä, vain debuggaamiseen jotta kuvat on rajattu oikein

                        masks_Data = r.masks
                        segmask = masks_Data.data[0].cpu().numpy()
                        color_coded_overlay_SAMsegmask(segmask, colorcoded_class) #letterboxed image

                        create_mask_yxz_labels(masks_Data, img_basename, classname, annotation_buffers)

                        resized_segmask = rescale_segmask_coordinates(segmask, original_img_w, original_img_h)
                        resized_segmask_np= torch.Tensor.numpy(resized_segmask)
                        finished_segmask_to_send = color_coded_overlay_SAMsegmask(resized_segmask_np, colorcoded_class)
                        batchlist_sam_images.append(finished_segmask_to_send)

                        metrics = MetricsSam(speed=r.speed)
                        samitems = samItems(finished_segmask=None, sam_metrics=metrics)
                        responseset = samResponse(image_name=img_basename, sam_items=[samitems], annotations=None)
                        response.append(responseset)
            print("length of response", len(response))
        encoded_images_to_send = encode_image_in_batch(batchlist_sam_images, samInference=True)

        curr_index = 0
        for response_schema in response:
            response_schema.sam_items[0].finished_segmask = encoded_images_to_send[curr_index]
            curr_index += 1


        annotations_payload = {
            name: buffer.getvalue()
            for name, buffer in annotation_buffers.items()
        }

        response[0].annotations = annotations_payload

        ta = TypeAdapter(samResponse)
        sendable = ta.dump_json(response)


        return sendable
    except Exception:
        logger.exception(f"sam inference failed for predict_id={predict_id}")
        return JSONResponse(
            status_code=500,
            content={"detail": "SAM inference failed. check logs"},
        )
