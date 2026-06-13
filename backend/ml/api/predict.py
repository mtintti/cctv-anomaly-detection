import httpx
from fastapi.routing import APIRouter
from fastapi import Depends
from ..dependecies import get_shared_client

router = APIRouter()

@router.get("/predict")
async def get_prediction():
    client = httpx.AsyncClient = Depends(get_shared_client)
    response = await client.get(f"predict/")