
import psycopg
from backend.app.config import logger
from ...dependecies import settings


async def create_item_in_database(id, name, near, municipality, coord1, coord2, date):
    async with await psycopg.AsyncConnection.connect(dbname=settings.db_name, user=settings.db_user, password=settings.db_pass,
                                                     host=settings.db_host, port=settings.db_port) as aconn:
        async with aconn.cursor() as curr:
            await curr.execute(
                "INSERT INTO cameras (id, name, near, municipality, longitude, latitude, date) Values (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING RETURNING id;",
                (id, name, near, municipality, coord1, coord2, date))
            rownum = await curr.fetchone()
            await aconn.commit()

            if rownum is not None:
                logger.info("Sending DB item, ", id)
            else:
                logger.info("the Database item is in, skipping...")


async def create_item_in_db_individual(invi_id, cam_id, pre_presname, pre_url, date):
    async with await psycopg.AsyncConnection.connect(dbname=settings.db_name, user=settings.db_user, password=settings.db_pass,
                                                     host=settings.db_host, port=settings.db_port) as aconn:
        async with aconn.cursor() as curr:
            await curr.execute(
                "INSERT INTO camera_individual (invi_id, cam_id, presname, url, date) Values (%s, %s, %s, %s, %s) ON CONFLICT (invi_id) DO UPDATE SET url = EXCLUDED.url, date = EXCLUDED.date",
                (invi_id, cam_id, pre_presname, pre_url, date))
            await aconn.commit()
