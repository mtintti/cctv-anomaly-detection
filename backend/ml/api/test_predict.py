import uuid
from time import sleep

import pytest

from backend.app.config import logger


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

