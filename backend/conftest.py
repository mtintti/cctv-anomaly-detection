
import httpx
import pytest_asyncio

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi_taskflow import TaskAdmin
from contextlib import asynccontextmanager

from backend.app.config import logmain
from backend.app.dependecies import shared_client, shared_client_close
from backend.app.services.db.database import open_pool
from backend.app.services.task_manager import task_manager

from backend.app.api import camera, stations, db_routes
from backend.ml.api.predict import router
from backend.ml.api.sam import sam_router


@pytest_asyncio.fixture
async def app():

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await shared_client(app)
        logmain()

        open_pool()

        yield

        await shared_client_close(app)

    app = FastAPI(lifespan=lifespan)

    TaskAdmin(app, task_manager)

    app.include_router(camera.router)
    app.include_router(stations.router)
    app.include_router(router)
    app.include_router(db_routes.router)
    app.include_router(sam_router)

    async with LifespanManager(app):
        yield app


@pytest_asyncio.fixture
async def testclient(app):
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost:8000"
    ) as client:
        yield client