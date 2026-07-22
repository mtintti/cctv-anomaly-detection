import asyncio
import base64
import time
import uuid
import httpx
import numpy as np
import onnxruntime
import starlette.datastructures
from PIL import Image
from io import BytesIO
import torch
import torchvision.ops as ops
from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException, BackgroundTasks
from pydantic import TypeAdapter
from redis.commands.search.query import Query

from backend.app import settings
from backend.app.config import logger, loggercrier
from backend.ml.api.letterboxing import letterbox, ImgSize
from backend.ml.api.onnxtoimg import onnx_to_img
from backend.ml.schema.json_response import JsonResponse, Inviprediction, Predictiondetails, PredictID
import redis

# Redis Client yhteyden tiedot, specifidattu settings:in kautta
r = redis.Redis(host=settings.redishost, port=settings.redisport, username=settings.redisusername, password=settings.redispassword)
if r:
    r.ping()
    logger.info("redis pinged!")
router = APIRouter()
sess = onnxruntime.InferenceSession(
    'backend/ml/best.onnx')

allowed_types = {'image/jpeg', 'image/png', 'application/pdf', 'text/plain', 'JPEG', 'PNG'}
max_size_allowed = 1024 * 1024 *25 #24mb

ml_inference_log = []
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
    # resizing original image size to onnx models expected/trained on input size of 512x512. we then change the 512x512 image to expected onnx models input in tensor form.
    # we return onnx model input, original image in PIL form, original images width, original images height
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
    # koska onnx model:in outputs eivät ole vielä mitenkään poistettu päälläkkäisyyksiä tehdään NMS
    # NMS käyttäen intersection-over-union poistaa samalla prediction confidence_scoren omaavat löydöt
    # jos niiden bbox:it ovat 60% tai enemmän limittäin poistamalla tupla löydöt pienellä heitolla
    reduced_output_indx = ops.nms(out0[:,0:4],prediction_scores,0.60)
    index_lookup = reduced_output_indx.tolist()
    pruned_output0 = []
    index = 0

    for x in range(len(output0)):
        if index_lookup[index] is x :
            pruned_output0.append(output0[x])
            index += 1

    out0arr = np.array(pruned_output0)

    boxes = out0arr[:,0:6]
    coeffincies_segmasks = out0arr[:,6:]
    segmasks_prototypes = output1

    final_composed_images, original_image_to_use = await onnx_to_img(boxes, coeffincies_segmasks, segmasks_prototypes, original_img_w, original_img_h, original_image, scale, pad, objects_found)
    ml_inference_log.append((time.perf_counter() - start_decodeimg) * 1000)
    return final_composed_images, original_image_to_use

#batclist_encodessa laitetaan löytöjen jsonmeta data (confidence_score, class_id ja belongsto..) Itse kuvat laitetaan tuple:een (bbox, segment, json_response)
async def batchlist_encode(belongto_name: str, objects_found: list, final_composed_images: list, item, batchlist, encoded_original_img, generated_predictID):

        logger.info(("length of final_composed_images ", len(final_composed_images)))
        start_batchlist = time.perf_counter()

        for z in range(len(final_composed_images)):
            invidual = final_composed_images[z]
            if (invidual.overlay_seg != None):
                # segmentmask ja bbox laitetaan PIL.Image.Image:na
                # koska ne muutetaan bufferin kautta base64 muotoon myöhemmin kun prediction tiedot on laitettu
                segmask = invidual.overlay_seg

                bbox = invidual.overlay_bbox

                confidencescore = objects_found[z].confidence_score
                class_id = objects_found[z].class_id
                class_name = objects_found[z].class_name
                print("encoded original ", type(encoded_original_img))


                predictions = Inviprediction(imageBbox=None, imageSeg=None)
                details = Predictiondetails(class_id=class_id, class_name=class_name,
                                                confidence_score=confidencescore)
                jsonresponse = JsonResponse(belongsto=belongto_name, original_img=None,
                                               details=[details],
                                               prediction=[predictions])
                constructed = PredictID(predict_id=generated_predictID, jsonresponse=[jsonresponse])
                batchlist.append(((bbox), (segmask), constructed))
                #json_response_all.append(constructed)
                #logger.info(("length of batchlist ", len(batchlist)))

            else:
                logger.info("skipped showing, results were none")
                predictions = Inviprediction(imageBbox=None, imageSeg=None)
                details = Predictiondetails(class_id=None, class_name=None, confidence_score=None)
                jsonresponse = JsonResponse(belongsto=belongto_name, original_img=None,
                                           details=[details],
                                           prediction=[predictions])
                constructed = PredictID(predict_id=generated_predictID, jsonresponse=[jsonresponse])  # {'imageBbox':bboxBytes}, {imageSeg:segmaskBytes}
                #json_response_all.append(constructed)
                print("constructed none path, ", constructed)
                batchlist.append(constructed)
            logger.debug(("length of batchlist ", len(batchlist)))

        timefromstart_batchlist = (time.perf_counter() - start_batchlist) * 1000
        ml_inference_log.append(timefromstart_batchlist)

# kuvat voivat suoraan näyttää <img> tagissä kun ne on muutettu data:imgage/png base64 muotoon bufferin kautta
def encode_image(image_tochange):
        #PIL.Image.Image muutetaan png byteksi
        buffer_touse = BytesIO()
        print("imgage_tochange type ", type(image_tochange))
        image_tochange.save(buffer_touse, format="PNG")
        changedto_Bytes = buffer_touse.getvalue()
        encoded_orig = base64.b64encode(changedto_Bytes)
        final_bytes_to_encoded_png = b'data:image/png;base64,' + encoded_orig
        return final_bytes_to_encoded_png# was this, using encoded ones, changedto_Bytes

async def encodeimageto_redis_json(batchlist, json_response_all, item: str | UploadFile, encoded_original, generated_predictID):
    try:
        # predict_id vertaa kyseisen lähetetyn /predict requestin tietoon, jokaiseen batchlist indexistä jossa on fintraffic kuva
        # ja/tai bbox + segmentmask generoidaan uniikki id (img:{predict_id}:{redisindex}:haluttukuva) jotta monet kuvasta olevat löydöt eivät indexoidu päällekkäin. Kuvat lähetetään Redis databaseen josta ne haetaan myöhemmin omilla id_illä
        for l in batchlist:
            redisindex = uuid.uuid4()
            logger.info(("redisuuid is encodeimagetojson ", redisindex))
            if type(l) == tuple:
                print("just l, ", l)
                print("what we want?? ", l[2])

                final_bytes_to_resBbox, final_bytes_to_resSeg = await asyncio.gather(
                    asyncio.to_thread(encode_image, l[0]), asyncio.to_thread(encode_image, l[1]))
                print("")
                print("final image bbox and seg are changed")
                print(type(final_bytes_to_resBbox), type(final_bytes_to_resSeg))
                print("first ten chars in both")
                print(final_bytes_to_resBbox[:80])
                print(final_bytes_to_resSeg[:80])
                print("final original image")
                print(type(encoded_original))
                print("first ten chars in original")
                print(encoded_original[:80])
                print("")
                try:
                    r.ft(f"img:{generated_predictID}:{redisindex}").dropindex(True)
                    logger.info("index was dropped in redis, was there already")
                except redis.exceptions.ResponseError:
                    logger.info("no redis index already present")
                    pass

                    try:
                        logger.info("trying redis main block")

                        try:
                            logger.info((f"trying to create redis index img{redisindex}"))
                            imgset = r.set(f"img:{generated_predictID}:{redisindex}:original_img", encoded_original, ex=240)
                            logger.info(imgset)
                            # bboxset = r.set("bbox", final_bytes_to_resBbox, 240)
                            bboxset = r.set(f"img:{generated_predictID}:{redisindex}:bbox", final_bytes_to_resBbox, ex=240)
                            logger.info(bboxset)
                            # segmaskset = r.set("segmask", final_bytes_to_resSeg, 240)
                            segmaskset = r.set(f"img:{generated_predictID}:{redisindex}:segmask", final_bytes_to_resSeg, ex=240)
                            logger.info(segmaskset)
                            #redisindex.create_index(schema, definition=IndexDefinition(prefix=["img:"], index_type=IndexType.JSON))
                        except redis.exceptions.ResponseError:
                            loggercrier.error(("error setting data ", imgset, bboxset, segmaskset))



                    except Exception:
                        loggercrier.error("error creating index/setting data redis")

                    l[2].jsonresponse[0].original_img = f"img:{generated_predictID}:{redisindex}:original_img"
                    l[2].jsonresponse[0].prediction[0].imageBbox = f"img:{generated_predictID}:{redisindex}:bbox"
                    l[2].jsonresponse[0].prediction[0].imageSeg = f"img:{generated_predictID}:{redisindex}:segmask"
                    print("type of l[0]", type(l[0]))
                    print("full l[0]", l[0])
                    print("jsonresponse img contains ", l[2].jsonresponse[0].original_img)
                    print("imagebbox contains ", l[2].jsonresponse[0].prediction[0].imageBbox)

                    #print("new")
                    #print(l[2].prediction)
                    # details = Predictiondetails()
                    constructed = l[2]
                    json_response_all.append(constructed)

            else:
                # löytöjä ei ollut, laitetaan vain alkuperinen kuva r.set(), sekä json_response_all:iin osoite
                imgset = r.set(f"img:{generated_predictID}:{redisindex}:original", encoded_original, ex=240)
                logger.info(imgset)
                l.jsonresponse[0].original_img = f"img:{generated_predictID}:{redisindex}:original_img"
                print("one original, results are none ", l.jsonresponse[0].original_img)
                json_response_all.append(l)


    except Exception:
        loggercrier("encoding image failed! ", exc_info=True)

## by id work, used by server component to get prediction_processing returned json.
# Json prediction sisältää bbox ja segmask Redis urlit, (img:{predict_id}:{redisindex}:haluttukuva)
@router.get("/predict/{predict_id}")
async def request_results(predict_id:uuid.UUID):
    found = None
    try:
        found = r.get(f"json_meta:{predict_id}:json")
    except redis.exceptions.ResponseError:
        logger.info("no redis index already present")

    if found is None:
        return {"none found" : predict_id}
    else:
        print("found json_meta in redis")
        print(found)
        print(type(found))
        return found

# haetaan redis predict_id indexissä olevat original, bbox ja segmask kuva bytes, jos indexiä ei ole palautetaan json none found.
@router.post("/predict/{predict_id}")
async def request_results(predict_id:uuid.UUID, redisURL: list[str] = Form(default=[])):
    try:
        logger.info("redis_URL gotten ")
        print("predict_id, ", predict_id," ", redisURL)
        for re in redisURL:
            print("redisURLS recived ", re)
        original_redisURL = redisURL[0]
        bbox_redisURL = redisURL[1]
        seg_redisURL = redisURL[2]
        found_Orig = None
        found_Bbox = None
        found_Seg = None
        try:
            logger.info(("redis_URL r.get() ", original_redisURL))
            found_Orig = r.get(f"{original_redisURL}") #.search(Query(f"{predict_id}"))

            logger.info(("redis_URL r.get() ", bbox_redisURL))
            found_Bbox = r.get(f"{bbox_redisURL}")

            logger.info(("redis_URL r.get() ", seg_redisURL))
            found_Seg = r.get(f"{seg_redisURL}")
        except redis.exceptions.ResponseError:
            logger.info("no redis index already present")

        if found_Orig is None or found_Bbox is None or found_Seg is None:

            return {
                "none found" : predict_id,
                "found_Orig" : found_Orig,
                "found_Bbox" : found_Bbox,
                "found_Seg":found_Seg
            }
        else:
            print("found json_meta in redis")
            print(type(found_Orig))
            print(type(found_Bbox))
            print(type(found_Seg))
            return found_Orig, found_Bbox, found_Seg
    except Exception:
        loggercrier.error("error in POST predict_id redis")



async def prediction_processing(generated_predictID, req: Request, file: list[UploadFile] = File(default=[]), url: list[str] = Form(default=[])): #file: UploadFile = File(...),
    try:

        toprocess = []
        json_response_all = []
        batchres = []
        batchlist = []
        print("files received:", [f.filename for f in file])
        print("urls received:", url)
        indx_for_url = 0
        print("cleared? ml_log ", len(ml_inference_log), " toprocess ",
              len(toprocess))
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
                bytes_from_img = await url_change_to_img(indx_for_url, req, url, client, batchres)
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

            final_composed_images, original_image_to_use = await get_predictions(res, original_image,
                                                                                   original_img_w, original_img_h,                                                              scale, pad, objects_found)

            start_originalencode = time.perf_counter()
            encoded = await asyncio.to_thread(encode_image, original_image_to_use)
            timefromstart_originalencode = (time.perf_counter() - start_originalencode) * 1000
            ml_inference_log.append(timefromstart_originalencode)

            await batchlist_encode(belongto_name, objects_found, final_composed_images, item,
                                   batchlist, encoded, generated_predictID)

        logger.info(("final batchlist length ", len(batchlist)))

        start_encode = time.perf_counter()
        await encodeimageto_redis_json(batchlist, json_response_all, item, encoded, generated_predictID)
        timefromstart_encode = (time.perf_counter() - start_encode) * 1000

        # final metrics after all images are shown
        ta = TypeAdapter(JsonResponse)
        sendable = ta.dump_json(json_response_all)
        print("sendables predict_id was ??", sendable[0], " that is the same as ", generated_predictID)
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

        #finaali json sendable on valmis kaikkien löydetyiden kuvien datalla,
        #jokaisen redis predict_id batchlistiin appended listasta on tehty redis set tallennus joten json responce_all lista tallennetaan redisiin.
        #Sendable json data haetaan @router.get("/predict/{predict_id}") requestissa saadulla predict_id:llä
        try:
            r.ft(f"json_meta:{generated_predictID}").dropindex(True)
            logger.info("index was dropped in redis, was there already")
        except redis.exceptions.ResponseError:
            logger.info("no redis index already present for json meta")
            pass

            logger.info("trying redis main block for sendable")

            try:
                logger.info((f"trying to create redis index json_meta{generated_predictID}..."))
                json_metaset = r.set(f"json_meta:{generated_predictID}:json", sendable, ex=240)
                logger.info(("setting json meta for ", generated_predictID, "json"))
                logger.info((json_metaset, f"json_meta:{generated_predictID}:json"))

            except redis.exceptions.ResponseError:
                loggercrier.error(("error setting jsonmeta data ", sendable))


    except Exception:
        loggercrier.error("error in /predict: ", exc_info=True)

# generoidaan /predict post requestin uniikki id (predict_id) jolla haetaan Get ja Post requestilla redisistä Json data sekä kuvien 64 encoded bytes
# prediction_processing laitetaan arqumenttina request, lähetetyt tiedostot ja fintraffic url joka suoritetaan taustalla. Background task ajetaan vasta kun predict_id on lähetetty return:in jälkeen
@router.post("/predict")
async def get_prediction(background_task: BackgroundTasks,req: Request, file: list[UploadFile] = File(default=[]), url: list[str] = Form(default=[])): #file: UploadFile = File(...),

    generated_predictID = uuid.uuid4()
    print("generated_predictID ", generated_predictID)
    print("type of id ", type(generated_predictID))
    background_task.add_task(prediction_processing, generated_predictID, req, file, url)
    return {"predict_id" : generated_predictID}



