import asyncio
import base64
import io
import os
import time
import uuid

import gevent
import onnxruntime
from PIL import Image
from starlette.datastructures import Headers, UploadFile
from starlette.requests import Request

os.environ["PSYCOPG_WAIT_FUNC"] = "wait_select"
import fakeredis
import requests

from backend.ml.api.predict import prediction_processing
from backend.testmockonnx import MockupOnnxInferenceSession

import psycopg
import psycopg_pool
from locust import task,events, between, HttpUser
from locust.runners import MasterRunner
from testcontainers.community.postgres import PostgresContainer

from backend.app.config import logger, loggercrier
from backend.app.main import app

sim_url = "https://weathercam.digitraffic.fi/C1255902.jpg" #"https://weathercam.digitraffic.fi/C1255909.jpg"
sim_file = "https://weathercam.digitraffic.fi/C1255902.jpg" #"https://weathercam.digitraffic.fi/C1255909.jpg"

# a standalone psycopg connection for datatables initalization
# for load testing using Locust as this happens just once per run

@events.init.add_listener
def using_database_TestContainer(environment, **kwargs):
    logger.info("staring locust load testing")
    if not isinstance(environment.runner, MasterRunner):
        print("Beginning test setup")
    else:
        print("Started test from Master node")
    logger.info(("enviroiment passed ", environment.stats))


    fakeserver = fakeredis.FakeServer()
    fr = fakeredis.FakeStrictRedis(server=fakeserver)
    app.state.r_redis = fr
    # Fakeredis käytetään testeihin oikean yhteyden sijaan

    app.state.sess_onnx = onnxruntime.InferenceSession('backend/ml/best.onnx')
    app.state.digi_traffic = HttpUser
    logger.info("staring locust load testing init ended")



def file_starlet_UploadFile_for_prediction():
    if getattr(app.state, "sim_upload_bytes", None) is None:
        logger.info(f"fetching sim prediction fixture from {sim_url}")
        response = requests.get(sim_url, timeout=10)
        response.raise_for_status()
        app.state.sim_upload_bytes = response.content
        app.state.sim_upload_content_type = response.headers.get("Content-Type", "image/jpeg")
        logger.info(f"sim prediction fixture fetched, size={len(app.state.sim_upload_bytes)} bytes")

    stream = io.BytesIO(app.state.sim_upload_bytes)
    headers = Headers({"content-type": app.state.sim_upload_content_type})

    try:
        return UploadFile(
            file=stream,
            size=len(app.state.sim_upload_bytes),
            filename=sim_file,
            headers=headers,
        )
    except TypeError:
        stream.seek(0)
        return UploadFile(
            filename=sim_file,
            file=stream,
            content_type=app.state.sim_upload_content_type,
            headers=headers,
        )

@events.init.add_listener
def init_sim_prediction_fixture(environment, **kwargs):
    try:
        file_starlet_UploadFile_for_prediction()
    except Exception:

        logger.error("error fetching sim prediction fixture", exc_info=True)


@events.quitting.add_listener
def _(environment, **kw):
    if environment.stats.total.fail_ratio > 0.01:
        loggercrier.error("Test failed due to failure ratio > 1%")
        environment.process_exit_code = 1
    elif environment.stats.total.avg_response_time > 300:
        loggercrier.error("Test failed due to average response time ratio > 300 ms")
        environment.process_exit_code = 1
    elif environment.stats.total.get_response_time_percentile(0.95) > 1000:
        loggercrier.error("Test failed due to 95th percentile response time > 1000 ms")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0

@events.quitting.add_listener
def cleanup_testcontainer(environment, **kwargs):
    sim_locust_pool_to_close = app.state.pool
    sim_locust_pool_to_close.close()
    container = app.state.TestContainer
    container.stop()
    loggercrier.info("stopped container and sim_locust_pool")


class users_db_interactions(HttpUser):
    wait_time = between(1,5)

    def on_start(self):
        # Jokainen virtuaalinen käyttäjä saa oman uniikin tunnuksen aloittaessaan
        self.sim_username_uuid = uuid.uuid4()
        self.sim_username_predecode = base64.urlsafe_b64encode(self.sim_username_uuid.bytes_le)
        logger.info(("sim user created,",self.sim_username_predecode))
        logger.info(("type of sim_username", type(self.sim_username_predecode)))
        self.sim_username = str(self.sim_username_predecode, 'utf-8')
        logger.info(("sim user to use,", self.sim_username))
        self.client.headers.update({"locust-db-loadtest": "true"})
        logger.info(("locust-db-loadtest is true?",self.client.headers.get("locust-db-loadtest")))

    @task(2)
    def creating_sim_user(self):
        logger.info("creating sim username")
        try:
            self.client.post("/auth/signup", json={'username':f"{self.sim_username}",'email': f"{self.sim_username}@g.cm", 'password': '111111'})
        except Exception:
            logger.error("error inserting sim user at API call", exc_info=True)

    @task(3)
    def sim_user_signin(self):
        try:
            logger.info("login in sim username")
            response = self.client.post("/auth/signin", json={'username':f"{self.sim_username}",'email': f"{self.sim_username}@g.cm", 'password': '111111'})

        except Exception:
            logger.error("error login in sim user at API call", exc_info=True)

    # koska oikea api endpoint /predict returnaa vain task_id ja prediction_id
    # process_prediction() olevan omassa functiossa, emme käytä oikeaa endponttia.
    # Testataan inputin preproccessoinnin, onnx inferenceä, segmenttimaskien tekemistä lifespan prewarm tavalla


def running_processing_in_own_thread():
    
    print("locust processing_prediction")
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/predict",
        "headers": [(b"host", b"app.local"), (b"content-length", b"3465")]
    }

    mock_sim_request = Request(scope=scope)
    file = [file_starlet_UploadFile_for_prediction()]

    # Safely handle the loop lifecycle within an isolated Gevent background thread
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        coro = prediction_processing(
            generated_predictID=uuid.uuid4(),
            req=mock_sim_request,
            file=file,
            url=[],
            do_redis=False,
            r=app.state.r_redis,
            onnx_sess=app.state.sess_onnx,
            # Note: client is passed, but ensure prediction_processing doesn't
            # attempt to call HttpUser like an active HTTP framework client.
            client=app.state.digi_traffic,
            return_for_locust=True
        )

        # Capture the direct output explicitly
        result = loop.run_until_complete(coro)
        return result
    except Exception as thread_exc:
        logger.error(f"Exception inside background thread execution", exc_info=True)
        return None
    finally:
        # Keep the loop alive for subsequent tasks or clean up gracefully without crashing
        pass


class prediction(HttpUser):

    #käytetään gvent threadiä koska async's and await's
    # aiheuttavata corutine ongelmia luokkan kanssa/sisällä locustissa
    @task(1)
    def processing_prediction(self):
        try:

            startofprocessing_predictloop = time.time()
            response_length = 0
            expection_happened = None
            response_process_thread = gevent.get_hub().threadpool.apply(running_processing_in_own_thread)
            print("response from locust processing")
            logger.info(response_process_thread)
            response_length = len(str(response_process_thread))

        except Exception as e:
            logger.error("Locust processing_prediction error, ", exc_info=True)
            expection_happened = e
        finally:
            gotten_whole_time = (time.time() - startofprocessing_predictloop) *1000
            events.request.fire(
                request_type="ASYNC",
                name="prediction_processing",
                response_time=gotten_whole_time,
                response_length=response_length,
                exception=expection_happened,
            )