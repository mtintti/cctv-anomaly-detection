
from fastapi import APIRouter, Request
from backend.app.services.db.database import get_user_in_db, insert_user_in_db

router = APIRouter(tags=["db"], responses={404: {"description": "not found :<"}})

@router.post("/auth/signin")
async def signin_attempt(request: Request):
    print("db_routes.py auth/login received ", request)
    user_data_to_try = await request.json()
    print("db_routes.py auth/login received data ", user_data_to_try)
    return await get_user_in_db(user_data_to_try)


@router.post("/auth/signup")
async def signin_attempt(request: Request):
    print("db_routes.py auth/signup received ", request)
    user_data_to_try = await request.json()
    print("db_routes.py auth/signup received data ", user_data_to_try)
    username = user_data_to_try['username']
    email = user_data_to_try['email']
    password = user_data_to_try['password']
    return await insert_user_in_db(username, email, password)
