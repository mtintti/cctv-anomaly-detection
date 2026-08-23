from asyncio import WindowsSelectorEventLoopPolicy

import httpx
import pytest_asyncio
import asyncio
import sys

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi_taskflow import TaskAdmin
from contextlib import asynccontextmanager

from starlette.requests import Request

from backend.app.config import logmain
from backend.app.dependecies import shared_client, shared_client_close
from backend.app.services.task_manager import task_manager

from backend.app.api import camera, stations, db_routes
from backend.ml.api.predict import router
from backend.ml.api.sam import sam_router

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

@pytest_asyncio.fixture
async def app():

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("asyncio get event loop policy is set as")
        print(asyncio.get_event_loop_policy().get_event_loop())
        ''' changed the event loop policy to try to get our async loop working with Psycopg but it still refuses to connect? 
        WARNING  psycopg.pool:pool_async.py:749 error connecting in 'pool-2': Psycopg cannot use the 'ProactorEventLoop' to run in async mode. 
        Please use a compatible event loop, for instance by setting 'asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())'
        '''
        await shared_client(app)
        logmain()


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