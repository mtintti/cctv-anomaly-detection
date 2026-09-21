import httpx
import onnxruntime
import psycopg
import psycopg_pool
from redis import asyncio
from gevent import lock
from starlette.requests import Request
from testcontainers.community.postgres import PostgresContainer

from . import settings
from .config import logger


# client on saatavilla globalisti moneen saman hostin api requestiin, clientti tehdään vain kerran
# host on laitettuna settings obj (Settings()) /config.py tiedostosta joka saa tiedot .env
# kun appi sammutetaan (lifestate = yield) -> client nollataan


def creating_sim_users_table(connection_info):
    #pool = sim_locust_pool
    with psycopg.connect(connection_info) as aconn:
        with aconn.cursor() as curr:
            try:
                logger.info("creating sim database table users..")

                curr.execute(
                    """ CREATE TABLE users (
                    id SERIAL PRIMARY KEY NOT NULL,
                    username VARCHAR(30),
                    email VARCHAR(40) UNIQUE,
                    password VARCHAR
                    )""")


                aconn.commit()
                logger.info("sim db table created!")

            except psycopg.Error as e:
                if e.diag:
                    print(f"SQLSTATE Code: {e.diag.sqlstate}")
                    print(f"Primary Message: {e.diag.message_primary}")
                    print(f"Severity: {e.diag.severity}")
                    print(f"Table Name: {e.diag.table_name}")
                    print(f"Constraint Name: {e.diag.constraint_name}")
                    print(f"Column Name: {e.diag.column_name}")
                logger.error("error inserting user", exc_info=True)
                logger.error("error creating sim user db table", exc_info=True)


def creating_sim_training_data_table(connection_info):
    with psycopg.connect(connection_info) as aconn:
        with aconn.cursor() as curr:
            try:
                logger.info("creating sim database table training_data..")

                curr.execute(
                    """ CREATE TABLE training_data_annotations (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id),
                    image_name TEXT,
                    training_img TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    annotations TEXT[]
                    )""")

                logger.info("inserting one sim fixture user + training_data row..")

                curr.execute(
                    """ INSERT INTO users (username, email, password)
                    VALUES (%s, %s, %s)
                    RETURNING id""",
                    ("sim_fixture_user", "sim_fixture_user@g.cm", "111111"))
                sim_fixture_user_id = curr.fetchone()[0]
                print("FIXTURE user", sim_fixture_user_id)

                curr.execute(
                    """ INSERT INTO training_data_annotations (user_id, image_name, training_img, annotations)
                    VALUES (%s, %s, %s, %s)""",
                    (
                        sim_fixture_user_id,
                        "https://weathercam.digitraffic.fi/C1255902.jpg",
                        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
                        ['{"classname": 4, "left": 10, "top": 10, "width": 50, "height": 50}'],
                    ))

                aconn.commit()
                logger.info("sim db training_data table + fixture row created!")

            except psycopg.Error as e:
                if e.diag:
                    print(f"SQLSTATE Code: {e.diag.sqlstate}")
                    print(f"Primary Message: {e.diag.message_primary}")
                    print(f"Severity: {e.diag.severity}")
                    print(f"Table Name: {e.diag.table_name}")
                    print(f"Constraint Name: {e.diag.constraint_name}")
                    print(f"Column Name: {e.diag.column_name}")
                logger.error("error creating sim training_data table / fixture row", exc_info=True)


async def shared_client(app):
    global client_digitraffic

    client_digitraffic = httpx.AsyncClient(
        base_url=settings.digitraffic_base,
        timeout=httpx.Timeout(10.0, connect=5.0),
        headers={"Accept": "application/json"},
    )
    client = httpx.AsyncClient()

    # Redis Client yhteyden tiedot, specifidattu settings:in kautta
    r = await asyncio.Redis(host=settings.redishost, port=settings.redisport, username=settings.redisusername,
                    password=settings.redispassword)
    app.state.r_redis = r

    connection_info = (
    f"dbname={settings.db_name} "f"user={settings.db_user} "f"password={settings.db_pass} "f"host={settings.db_host} "f"port={settings.db_port}")
    pool = psycopg_pool.AsyncConnectionPool(connection_info, max_size=20, open=False)

    sess = onnxruntime.InferenceSession('backend/ml/best.onnx')

    app.state.digi_traffic = client_digitraffic
    app.state.client = client
    app.state.r_redis = r
    app.state.sess_onnx = sess
    app.state.pool = pool
    app.state.have_used_test_container_before = lock.Semaphore(0)

    print("\n stats: ")
    print(app.state.pool.get_stats())
    #pool_to_use = app.state.pool
    await app.state.pool.open()
    await app.state.pool.wait()

    print("\n ")
    print("connection pool is opened")
    print(app.state.pool)


    print("\n ..dependencies done: ", client_digitraffic, client, r, sess, pool)


#shared connections set at start-up / lifespan
def get_digitraffic_connection(request:Request):
    digitraffic_conn = request.app.state.digi_traffic
    return digitraffic_conn

def get_client_connection(request:Request):
    client_conn = request.app.state.client
    return client_conn

def get_redis_connection(request:Request):
    redis_conn = request.app.state.r_redis
    return redis_conn

def get_fake_redis_connection(request:Request):
    fake_redis_conn = request.app.state.fake_redis
    return fake_redis_conn

def get_onnx_sess(request:Request):
    onnx_path = request.app.state.sess_onnx
    return onnx_path

async def get_pool(request:Request):
    logger.info(("app.state.pool contains",request.app.state.pool))
    logger.info(("all app.state items",request.app.state._state))
    should_use_sim_locust_db_pool = request.headers.get("locust-testContainer-db-loadtest") == "true"
    logger.info(request.headers.keys())
    logger.info(("locust-db-loadtest in main's side?? ",request.headers.get("locust-testContainer-db-loadtest")))
    logger.info(should_use_sim_locust_db_pool)
    if should_use_sim_locust_db_pool:

        if request.app.state.have_used_test_container_before.counter == 0:
            request.app.state.have_used_test_container_before = lock.Semaphore(1)
            logger.info(("locking ", request.app.state.have_used_test_container_before.counter))
            container = PostgresContainer("postgres:16-alpine")
            container.start()
            connection_info = (
                f"dbname={container.dbname} "f"user={container.username} "f"password={container.password} "f"host={container.get_container_host_ip()} "f"port={container.get_exposed_port(5432)}")

            creating_sim_users_table(connection_info)
            creating_sim_training_data_table(connection_info)
            logger.info("creating_sim users and training_data_table finished in init")

            # käytetään ConnectionPoolia simuloituun Locust trafficiin.
            sim_locust_pool = psycopg_pool.AsyncConnectionPool(connection_info, max_size=20, open=False)

            await sim_locust_pool.open()
            await sim_locust_pool.wait()
            logger.info("app state contents")
            logger.info(request.app.state._state)
            request.app.state.pool = sim_locust_pool
            request.app.state.TestContainer = container
            logger.info(("sim_locust_pool connection ", sim_locust_pool.connection))
            #request.app.state.container_locked = lock.Semaphore(0)
            logger.info(("locking after ", request.app.state.have_used_test_container_before.counter))

            return sim_locust_pool
        else:
            logger.info(("have_used_test_container_before is locked?", request.app.state.have_used_test_container_before.counter))
            sim_locust_pool = request.app.state.pool
            logger.info(("sim_locust_pool connection, already turned on ", sim_locust_pool.connection))
            return sim_locust_pool
    else:
        logger.info("non locust db request, using real pg AsyncConnectionPool")
        postgres_pool = request.app.state.pool
        return postgres_pool


async def shared_client_close(app) -> None:
    to_close = app.state.digi_traffic
    await to_close.aclose()

    to_close2 = app.state.client
    await to_close2.aclose()

    to_close3 = await app.state.r_redis
    await to_close3.close()

    to_close5 = app.state.pool
    await to_close5.close()


    if app.state.TestContainer is not None:
        app.state.have_used_test_container_before = lock.Semaphore(0)
        logger.info(("unlocking done", app.state.have_used_test_container_before.counter))
        container = app.state.TestContainer
        container.stop()
        logger.info("stopped container and sim_locust_pool")

