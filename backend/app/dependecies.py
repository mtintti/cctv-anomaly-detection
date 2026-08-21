import fakeredis
import httpx
import onnxruntime
import psycopg_pool
import redis
from starlette.requests import Request

from . import settings
from .config import logger


# client on saatavilla globalisti moneen saman hostin api requestiin, clientti tehdään vain kerran
# host on laitettuna settings obj (Settings()) /config.py tiedostosta joka saa tiedot .env
# kun appi sammutetaan (lifestate = yield) -> client nollataan

async def shared_client(app):
    global client_digitraffic

    client_digitraffic = httpx.AsyncClient(
        base_url=settings.digitraffic_base,
        timeout=httpx.Timeout(10.0, connect=5.0),
        headers={"Accept": "application/json"},
    )
    client = httpx.AsyncClient()

    # Redis Client yhteyden tiedot, specifidattu settings:in kautta
    r = redis.Redis(host=settings.redishost, port=settings.redisport, username=settings.redisusername,
                    password=settings.redispassword)
    #Fakeredis käytetään testeihin oikean yhteyden sijaan
    fakeserver = fakeredis.FakeServer()
    fr = fakeredis.FakeStrictRedis(server=fakeserver)

    connection_info = (
        f"dbname={settings.db_name} "f"user={settings.db_user} "f"password={settings.db_pass} "f"host={settings.db_host} "f"port={settings.db_port}")
    pool = psycopg_pool.AsyncConnectionPool(connection_info, open=False)

    sess = onnxruntime.InferenceSession('backend/ml/best.onnx')
    app.state.digi_traffic = client_digitraffic
    app.state.client = client
    app.state.r_redis = r
    app.state.fake_redis = fr
    app.state.sess_onnx = sess
    app.state.pool = pool
    print("\n[FakeRedis]")
    print(f"server: {fakeserver}")
    print("")
    print(f"server connected?: {fakeserver.connected}")
    print("")
    print(f"redis: {fr}")
    print("")
    print(f"setted as in app.state: {app.state.fake_redis}")


    print("\n ..dependencies done: ", client_digitraffic, client, r, fr, sess, pool)


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

def get_pool():
    from .main import app
    logger.info(("app.state.pool contains",app.state.pool))
    postgres_pool = app.state.pool
    return postgres_pool


async def shared_client_close(app) -> None:
    to_close = app.state.digi_traffic
    to_close.aclose()

    to_close2 = app.state.client
    to_close2.aclose()

    to_close3 = app.state.r_redis
    to_close3.close()

    to_close4 = app.state.fake_redis
    to_close4.close()

    to_close5 = app.state.pool
    to_close5.close()

