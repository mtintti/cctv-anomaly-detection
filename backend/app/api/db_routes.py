
from fastapi import APIRouter, Request
from fastapi.params import Depends

from backend.app.config import logger
from backend.app.dependecies import get_pool
from backend.app.schemas.get_recents_training_data import Recents_training_data
from backend.app.schemas.login import Login
from backend.app.schemas.signin import Signup
from backend.app.services.db.database import get_user_in_db, insert_user_in_db, inserting_pg_training, \
    get_postgres_training_recents

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

@router.get("/auth/get_postgres_training_recents/{email}")
async def get_recent_user_training_data(request:Request,email:str, pool = Depends(get_pool)):
    print("email in /auth/get_postgres_training_recents/", email)
    gotten_from_db = await get_postgres_training_recents(pool, email)
    all_validated = []
    for r in gotten_from_db:
        validated_by_schema = Recents_training_data(id=r[0],image_name=r[1], training_img=r[2], updated_at=r[3] ,annotations=r[4])
        #print("validated_by_schema", validated_by_schema)
        all_validated.append(validated_by_schema)
    return all_validated
