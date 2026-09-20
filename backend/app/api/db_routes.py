import json

from fastapi import APIRouter, Request
from fastapi.params import Depends

from backend.app.config import logger
from backend.app.dependecies import get_pool
from backend.app.schemas.get_recents_training_data import Recents_training_data
from backend.app.schemas.locust_metrics_real_db import Locust_to_postgres
from backend.app.schemas.login import Login
from backend.app.schemas.signin import Signup
from backend.app.services.db.database import get_user_in_db, insert_user_in_db, inserting_pg_training, \
    get_postgres_training_recents, inserting_locust_comparison_metrics, getting_proxy_metrics_for_groundtruth, \
    inserting_users_set_dataset_content

router = APIRouter(tags=["db"], responses={404: {"description": "not found :<"}})

@router.post("/auth/signin")
async def signin_attempt(request: Request, pool = Depends(get_pool)):

    user_data_to_try = await request.json()
    email = user_data_to_try['email']
    password = user_data_to_try['password']
    user_data_validated = Login(email=email, password=password)
    return await get_user_in_db(pool, user_data_validated.model_dump())


@router.post("/auth/signup")
async def signup_attempt(request: Request, pool = Depends(get_pool)):
    logger.debug(("datapool is ", pool))
    user_data_to_try = await request.json()
    username = user_data_to_try['username']
    email = user_data_to_try['email']
    password = user_data_to_try['password']

    user_data_validated = Signup(username=username, email=email, password=password)
    valid_to_use = user_data_validated.model_dump()
    username_valid = valid_to_use['username']
    email_valid = valid_to_use['email']
    password_valid = valid_to_use['password']
    return await insert_user_in_db(pool, username_valid, email_valid, password_valid)


@router.post("/auth/insert_postgres_training")
async def inserting_training_data_users(request:Request, pool = Depends(get_pool)):
    recived_sam_annonations = await request.json()
    #print("gotten auth/insert_pg_train", recived_sam_annonations)
    session_user_email = recived_sam_annonations.get('user_email')
    print("user_email in auth/insert_training", session_user_email)
    constructing_training_data = recived_sam_annonations.get("constructing_training_data")
    return await inserting_pg_training(pool, constructing_training_data, session_user_email)

#email is set from frontend/api/auth/db_recents/route file using users session email set at login/signin token: ${session.user.email}
@router.get("/auth/get_postgres_training_recents")
async def get_recent_user_training_data(request:Request, pool = Depends(get_pool)):
    email = request.headers.get('session_email')
    print("email in /auth/get_postgres_training_recents/", email)
    if email is not None:
        gotten_from_db = await get_postgres_training_recents(pool, email)
        all_validated = []
        for r in gotten_from_db:
            validated_by_schema = Recents_training_data(id=r[0],image_name=r[1], training_img=r[2], updated_at=r[3] ,annotations=r[4])
            #print("validated_by_schema", validated_by_schema)
            all_validated.append(validated_by_schema)
        return all_validated
    elif email is None:
        return {'session_email_incorrect':email}

@router.post("/auth/metrics_to_pg_from_locust")
async def inserting_locust_metrics_for_pred_comparison(request:Request,sendable: Locust_to_postgres, pool = Depends(get_pool)):
    print("in /auth/metrics_to_pg_from_locust route")
    print("gotten_from_locust", sendable)
    job_id_locust_insert = sendable.job_id
    job_predict_id_insert = sendable.jobs_predict_id
    job_classnumer_id = sendable.class_id
    job_confidence_score = sendable.confidence_score
    image_file_handling = sendable.image_file_handling
    preprocess_to_tensor = sendable.preprocess_to_tensor
    inference = sendable.inference
    bbox_and_segmask = sendable.bbox_and_segmask
    original_img_encode = sendable.original_img_encode
    batchlist_creation = sendable.batchlist_creation
    encode_images = sendable.encode_images
    redis = sendable.redis
    whole_runs_time = sendable.whole_runs_time
    if job_id_locust_insert <= 100:

        insertable = Locust_to_postgres(job_id=job_id_locust_insert, jobs_predict_id=job_predict_id_insert, class_id=job_classnumer_id, confidence_score=job_confidence_score,
                                        image_file_handling=image_file_handling, preprocess_to_tensor=preprocess_to_tensor, inference=inference,
                                        bbox_and_segmask=bbox_and_segmask, original_img_encode=original_img_encode, batchlist_creation=batchlist_creation,
                                        encode_images=encode_images, redis=redis,whole_runs_time=whole_runs_time)
        return await inserting_locust_comparison_metrics(pool, insertable.model_dump(mode="json"))
    else:
        return {'inserts are too large. stopping': job_id_locust_insert}
@router.post("/auth/send_to_user_dataset")
async def sending_content_to_user_dataset(request:Request, pool=Depends(get_pool)):
    print("sending_content_to_user_dataset")
    sendable = await request.json()
    #sendable = json.load(sendable_pre_parsing)
    print("sendable")
    print("type of sendable", type(sendable))
    #print(sendable['sendable'])
    email = request.headers.get('session_email')
    dataset_name = request.headers.get('dataset_name')
    return await inserting_users_set_dataset_content(sendable['sendable'], pool, session_user_email=email, dataset_name=dataset_name)

@router.post("/auth/proxy_metrics_from_url_image")
async def proxy_metrics_from_url_image(image_name: str,pool=Depends(get_pool)):
    logger.info(("pool in proxy route is ", pool))
    logger.info(("image_name in proxy route is ", image_name))
    return await getting_proxy_metrics_for_groundtruth(pool, image_name)