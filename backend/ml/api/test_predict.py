import base64
import uuid
from time import sleep
from types import SimpleNamespace

import pytest
from PIL import Image

from backend.app.config import logger
from backend.ml.api.predict import encode_image_in_batch, batchlist_encode, encode_image


class TestClass_predict:
    @pytest.mark.asyncio
    async def test_predict_poll_until_complete(self, testclient):
        predict_test_id = uuid.uuid4()
        logger.info("predictTests/test_predict_poll")
        response = await testclient.post("/predict",
                                         data={"generated_predictID": str(predict_test_id), "do_redis": True,
                                               "fake_redis_for_tests": True,
                                               "url": ["https://weathercam.digitraffic.fi/C1255902.jpg"], }, )
        logger.info(("response of POST", response.json()))
        res = response.json()
        predict_test_id = res['predict_id']
        task_id = res['id of task']
        numbers_to_try = 0
        waiting_time_set = None
        while numbers_to_try == 0 or numbers_to_try < 3:
            if waiting_time_set == None:
                task_id_response = await testclient.post(f"/predict/{predict_test_id}/{task_id}",
                                                         data={"fake_redis_for_tests": True, }, )
                logger.info(("task_id_response", task_id_response.json()))
                taskid_json = task_id_response.json()
                numbers_to_try += 1
                if task_id_response.headers.get('retry-after') == str and taskid_json['record by id of task'][
                    'status'] == 'success':
                    # taking the headers as they are, would mean we pause for 3000 not 3 seconds
                    logger.debug(("HEADERS GOTTEN", task_id_response.headers.get('retry-after')))
                    waiting_time_set = 3
                    print("numbers_to_try", numbers_to_try)
            else:
                sleep(waiting_time_set)
                task_id_response = await testclient.post(f"/predict/{predict_test_id}/{task_id}",
                                                         data={"fake_redis_for_tests": True, }, )
                logger.info(("task_id_response AFTER SLEEP", task_id_response.json()))
                taskid_json = task_id_response.json()
                print("numbers_to_try", numbers_to_try)
                numbers_to_try += 1
                if task_id_response.headers.get('retry-after') == str and taskid_json['record by id of task'][
                    'found'] == None:
                    logger.debug(("HEADERS GOTTEN", task_id_response.headers.get('retry-after')))
                    waiting_time_set = 3
                    print("type of waiting_time_set", type(waiting_time_set))
                else:
                    print(taskid_json['record by id of task'])
                    assert taskid_json['record by id of task']['status'] == 'success'
                    assert taskid_json['record by id of task']['found'] == type(list)
                    break

    @pytest.mark.asyncio
    async def test_predict_both_not_found_in_redis(self, testclient):
        predict_test_id = uuid.uuid4()
        logger.info("predictTests/test_predict_poll")
        response = await testclient.post("/predict",
                                         data={"generated_predictID": str(predict_test_id), "do_redis": True,
                                               "fake_redis_for_tests": True,
                                               "url": ["https://weathercam.digitraffic.fi/C1255902.jpg"], }, )
        logger.info(("response of POST", response.json()))
        predict_test_id_false = '708067ec-d791-4020-8318-f4573d69837e'
        task_id_false = '8f9d0fb7-4f89-43ac-a11f-ad290eeace1a'
        task_id_response = await testclient.post(f"/predict/{predict_test_id_false}/{task_id_false}",
                                                 data={"fake_redis_for_tests": True, }, )
        logger.info(("task_id_response", task_id_response.json()))
        taskid_json = task_id_response.json()
        print("status code ", task_id_response.status_code)
        assert taskid_json['detail'] == 'Not Found'


class TestPredict_just_using_API:

    @pytest.mark.asyncio
    async def test_predict_creates_task(self, testclient):
        predict_id = uuid.uuid4()

        response = await testclient.post(
            "/predict",
            data={
                "generated_predictID": str(predict_id),
                "do_redis": "true",
                "fake_redis_for_tests": "true",
                "url": "https://weathercam.digitraffic.fi/C1255902.jpg",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["predict_id"] == str(predict_id)
        assert "id of task" in body

class TestEncoding:

    def test_encode_image_returns_png_data_uri(self):
        image = Image.new("RGB", (20, 20), "red")

        result = encode_image(image)

        assert result.startswith(b"data:image/png;base64,")

        encoded_part = result.split(b",", 1)[1]
        decoded = base64.b64decode(encoded_part)

        assert decoded.startswith(b"\x89PNG")

    def test_encode_image_in_batch_handles_bbox_segmask_tuples(self):
        images = [
            (
                Image.new("RGB", (20, 20), "red"),
                Image.new("RGB", (20, 20), "blue"),
            )
        ]

        result = encode_image_in_batch(images)

        assert len(result) == 1
        assert isinstance(result[0], tuple)
        assert len(result[0]) == 2

        assert result[0][0].startswith(
            b"data:image/png;base64,"
        )
        assert result[0][1].startswith(
            b"data:image/png;base64,"
        )

    def test_encode_image_in_batch_sam_mode(self):
        images = [(
            Image.new("RGB", (20, 20), "red"),
            Image.new("RGB", (20, 20), "blue"),
            )
        ]

        result = encode_image_in_batch(
            images,
            samInference=True,
        )

        assert len(result) == 1
        assert result[0][0].startswith(
            b"data:image/png;base64,"
        )


class TestBatchlistEncode:

    @pytest.mark.asyncio
    async def test_batchlist_encode_with_prediction(self):
        overlay = SimpleNamespace(
            overlay_seg=Image.new("RGB", (20, 20), "white"),
            overlay_bbox=Image.new("RGB", (20, 20), "black"),
        )

        detected_object = SimpleNamespace(
            confidence_score=0.876,
            class_id=1,
            class_name="pothole",
        )

        batchlist = []
        inference_log = []

        await batchlist_encode(
            "camera.jpg",
            [detected_object],
            [overlay],
            "camera.jpg",
            batchlist,
            "b'data:image/png;base64,",
            uuid.uuid4(),
            640,
            480,
            inference_log,
        )

        assert len(batchlist) == 1

        item = batchlist[0]

        assert isinstance(item, tuple)
        assert len(item) == 3

        assert item[2].jsonresponse[0].details[0].class_id == 1
        assert item[2].jsonresponse[0].details[0].class_name == "pothole"

        assert len(inference_log) == 1

    @pytest.mark.asyncio
    async def test_batchlist_encode_without_prediction(self):
        overlay = SimpleNamespace(
            overlay_seg=None,
            overlay_bbox=None,
        )

        batchlist = []
        inference_log = []

        predict_id = uuid.uuid4()

        await batchlist_encode(
            "camera.jpg",
            [],
            [overlay],
            "camera.jpg",
            batchlist,
            "b'original-image",
            predict_id,
        1240,
            780,
            inference_log,
        )

        assert len(batchlist) == 1

        result = batchlist[0]

        assert result.predict_id == predict_id
        assert result.jsonresponse[0].original_img == "b'original-image"
        assert result.jsonresponse[0].details[0].class_id is None