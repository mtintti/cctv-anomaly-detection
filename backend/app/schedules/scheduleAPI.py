from time import sleep
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ..dependecies import get_shared_client
from backend.app.config import logger, loggercrier
from ..services.db.database import create_item_in_database, create_item_in_db_individual
from ..services.fintraffic import all_stations, camera_station
from .timehelper import get_time

scheduler = AsyncIOScheduler()
wanted_target = ["id"]

# haetaan Stations fintraffic id nimet, coordinaatit, properties, yms,
# databasen halutut tiedot ja lähetetään ne SQL kutsulla databaseen.
# AsyncScheduler tapahtuu backgroundissa jotten ei estä ohjelman käyttöä. Job_id:ssä alustetaan def task tapahtuvan 30min välein

# db_individual on kamera station eri suuntiin varten + tienpinta, itse url osoite ja presentaatio nimi kameran kuvalle
# API datassa voi olla vain 1 kamera kuvakulma tai enemmänkin.

async def cameraAPIcall(idstring):
    camerares = await camera_station(idstring, get_shared_client())
    camres = camerares.dict()
    starttime = get_time()
    id = camres["id"]
    coordinates = camres["geometry"]["coordinates"]
    coord1 = coordinates[0]
    coord2= coordinates[1]
    coord3 = coordinates[2]

    prop = camres["properties"]
    name = prop["name"]
    near = (prop["nearestWeatherStationId"])
    municipality = (prop["municipality"])
    pre = prop["presets"]
    prelength = len(pre)
    date = get_time()
    await create_item_in_database(id, name, near, municipality, coord1, coord2, date)
    for _ in range(0, prelength):
        pre_ = (pre[_])
        pre_id = pre_["id"]
        cam_id = id
        pre_presname = pre_["presentationName"]
        pre_url: str = pre_["imageUrl"]
        date = get_time()
        await create_item_in_db_individual(pre_id, cam_id, pre_presname, pre_url, date)
    print("sending database creation..")

    lasttime = get_time()

# haetaan kameroiden station ja tarkemmat suunta kohtaiset tiedot 50 cycleissä
# koska fintraffic estää liialliset (>60 per min) API kutsut sen takia tauko
async def task():
    print("starting api call")
    logger.info("starting station API from task")
    data = await all_stations(get_shared_client())
    data_res = data.model_dump()
    count = 0
    total_calls = 0
    try:
        id_num = ([station[wanted_target[0]] for station in data_res["features"]])
        stationsSize = len(id_num)
        logger.info("id of station got from task")
        for i in range(0, len(id_num)):
            idstring = id_num.pop(0)
            count += 1
            if count > 50:
                logger.debug("sleeping.. API task limit reached")
                sleep(65)
                total_calls += count
                count = 0
                await cameraAPIcall(idstring)
            else:
                await cameraAPIcall(idstring)
        logger.info("ScheduleAPI ended. The total stations went -> ", i)


    except Exception as e:
        loggercrier.error("Task error happened after try: extract call", exc_info=True)

job_id = scheduler.add_job(task, "interval", minutes=30)

def start_timer():
    scheduler.start()
