
from backend.app.config import logger


async def create_item_in_database(pool, id, name, near, municipality, coord1, coord2, date):
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


async def create_item_in_db_individual(pool, invi_id, cam_id, pre_presname, pre_url, date):
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            await curr.execute(
                "INSERT INTO camera_individual (invi_id, cam_id, presname, url, date) Values (%s, %s, %s, %s, %s) ON CONFLICT (invi_id) DO UPDATE SET url = EXCLUDED.url, date = EXCLUDED.date",
                (invi_id, cam_id, pre_presname, pre_url, date))
            await aconn.commit()


async def get_user_in_db(pool,using_to_search):
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


async def insert_user_in_db(pool, username: str, email: str, password: int):
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            try:
                await curr.execute("""INSERT INTO users (username, email, password) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING RETURNING id""",
                    (username, email, password) )

                user_exists = await curr.fetchone()
                await aconn.commit()
                print("user_exists? ", user_exists)
                if user_exists is None:
                    print("Email already exists")
                    return None
                else:
                    user_id = user_exists[0]
                    print("Created user:", user_id)
                    return user_id


            except Exception:
                logger.error("error inserting user", exc_info=True)

async def inserting_pg_training(pool, constructued_training_data,user_email: str):
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            try:
                await curr.execute("SELECT id FROM users WHERE email = %s", (user_email,))
                user_row = await curr.fetchone()
                if user_row is None:
                    print("user not found, inserting_pg_training")
                    logger.info(("training upload rejected, unknown user email ", user_email))
                    return None
                else:
                    user_id = user_row[0]
                    #user_username = user_row[1]
                    print("user_row all", user_row)
                    print("user found in db, inserting training data for ",user_id)


            except Exception:
                logger.error("error inserting training_data", exc_info=True)

