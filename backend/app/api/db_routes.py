
from fastapi import APIRouter, Request
from fastapi.params import Depends

from backend.app.config import logger
from backend.app.dependecies import get_pool
from backend.app.schemas.login import Login
from backend.app.schemas.signin import Signup
from backend.app.services.db.database import get_user_in_db, insert_user_in_db

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
