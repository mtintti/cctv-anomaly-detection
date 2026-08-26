import sys

import fakeredis
import httpx
import psycopg_pool
import pytest_asyncio
import asyncio

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi_taskflow import TaskAdmin
from contextlib import asynccontextmanager
from testcontainers.community.postgres import PostgresContainer
from app.config import logmain, logger
from app.services.task_manager import task_manager

from app.api import camera, stations, db_routes
from ml.api.predict import router
from ml.api.sam import sam_router
from testmockonnx import MockupOnnxInferenceSession

container = PostgresContainer("postgres:16-alpine")

if sys.platform == 'win32':
    from asyncio import WindowsSelectorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

@pytest_asyncio.fixture(scope="session")
async def test_container():
    logger.info("opening test db container..")
    logger.info(("container is ", container))
    logger.info(("status: ", container.status))

    container.start()
    yield container
    container.stop()

@pytest_asyncio.fixture(scope="session")
async def test_pool(test_container):
    logger.info("opening test db pool..")
    logger.info(test_container.status)
    connection_info = (
        f"dbname={test_container.dbname} "f"user={test_container.username} "f"password={test_container.password} "f"host={test_container.get_container_host_ip()} "f"port={test_container.get_exposed_port(5432)}")
    pool = psycopg_pool.AsyncConnectionPool(connection_info, open=False)
    await pool.open()
    await pool.wait()
    yield pool
    await pool.close()

@pytest_asyncio.fixture(scope="session")
async def creating_test_users_table(test_pool):
    pool = test_pool
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            try:
                logger.info("creating database table users..")
                await curr.execute(
                    """ CREATE TABLE users (
                    id SERIAL NOT NULL,
                    username VARCHAR(20),
                    email VARCHAR(30) UNIQUE,
                    password VARCHAR
                    )""")

                await aconn.commit()
                logger.info("db table created!")

            except Exception:
                logger.error("error creating test user db table", exc_info=True)


@pytest_asyncio.fixture
async def app(test_pool, creating_test_users_table):

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("asyncio get event loop policy is set as")
        logger.info(asyncio.get_event_loop_policy().get_event_loop())

        # Fakeredis käytetään testeihin oikean yhteyden sijaan
        fakeserver = fakeredis.FakeServer()
        fr = fakeredis.FakeStrictRedis(server=fakeserver)
        app.state.fake_redis = fr

        app.state.r_redis = fr
        app.state.sess_onnx = MockupOnnxInferenceSession()

        client = httpx.AsyncClient()
        app.state.client = client

        logger.info(("checking connection info", test_pool.conninfo))
        app.state.pool = test_pool

        logmain()


        yield

        #await shared_client_close(app)
        to_close4 = app.state.fake_redis
        to_close4.close()
        to_close5 = app.state.pool
        to_close5.close()

    app = FastAPI(lifespan=lifespan)

    TaskAdmin(app, task_manager)

    app.include_router(camera.router)
    app.include_router(stations.router)
    app.include_router(sam_router) #router was last, caused starlet mixup on routes /predict and /predict/sam
    app.include_router(router)
    app.include_router(db_routes.router)

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