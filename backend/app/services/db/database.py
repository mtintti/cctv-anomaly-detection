
import psycopg_pool
from backend.app.config import logger
from ...dependecies import settings


connection_info = (f"dbname={settings.db_name} "f"user={settings.db_user} "f"password={settings.db_pass} "f"host={settings.db_host} "f"port={settings.db_port}")
pool = psycopg_pool.AsyncConnectionPool(connection_info, open=False)

async def open_pool():
    print("\n stats: ")
    print(pool.get_stats())
    await pool.open()
    await pool.wait()
    print("\n ")
    print("connection pool is opened")


async def create_item_in_database(id, name, near, municipality, coord1, coord2, date):
        async with pool.connection() as aconn:
            print(pool.check())
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
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            await curr.execute(
                "INSERT INTO camera_individual (invi_id, cam_id, presname, url, date) Values (%s, %s, %s, %s, %s) ON CONFLICT (invi_id) DO UPDATE SET url = EXCLUDED.url, date = EXCLUDED.date",
                (invi_id, cam_id, pre_presname, pre_url, date))
            await aconn.commit()
