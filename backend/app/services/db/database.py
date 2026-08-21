
from backend.app.config import logger
from backend.app.dependecies import get_pool


async def open_pool():
    pool_opened = get_pool()
    print("\n stats: ")
    print(pool_opened.get_stats())
    await pool_opened.open()
    await pool_opened.wait()

    print("\n ")
    print("connection pool is opened")
    print(pool_opened)


async def create_item_in_database(id, name, near, municipality, coord1, coord2, date):
        pool = get_pool()
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
    pool = get_pool()
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            await curr.execute(
                "INSERT INTO camera_individual (invi_id, cam_id, presname, url, date) Values (%s, %s, %s, %s, %s) ON CONFLICT (invi_id) DO UPDATE SET url = EXCLUDED.url, date = EXCLUDED.date",
                (invi_id, cam_id, pre_presname, pre_url, date))
            await aconn.commit()


async def get_user_in_db(using_to_search):
    pool = get_pool()
    print("pool_opened is set as", pool)
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            print("gotten ", using_to_search)
            email = using_to_search['email']
            print(("email ", email))
            await curr.execute(f"SELECT * FROM users WHERE email = %s", (email,))
            #user_to_return= await aconn.commit()
            user_to_return = await curr.fetchone()
            if user_to_return:
                print("user gotten from db")
                print(user_to_return)
                return user_to_return
            else:
                print("user was not found, from db")
                return


async def insert_user_in_db(username: str, email: str, password: int):
    pool = get_pool()
    print("pool_opened is set as", pool)
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:

            await curr.execute(f"INSERT INTO users (username, email, password) Values (%s, %s, %s)",
                               (username, email, password))
            await aconn.commit()
