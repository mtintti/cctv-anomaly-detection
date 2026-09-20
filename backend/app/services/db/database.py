import psycopg

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


            except psycopg.Error as e:

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


                    try:
                        print("user found in db, inserting training data for ", user_id)
                        image_name = None
                        training_img = None
                        annotations = None
                        successful_inserts = 0
                        for i in constructued_training_data[0]:
                            print("type of i", type(i))
                            print(i.keys())
                            if i.get('image_name'):
                                image_name = i.get('image_name')
                                print("data to insert", image_name)
                            if i.get('training_img'):
                                training_img = i.get('training_img')
                            if i.get('annonations'):
                                annotations = i.get('annonations')

                            if image_name is not None and training_img is not None and annotations is not None:
                                print("data to insert", image_name, " ", len(training_img), " ", len(annotations))
                                print("type of annotations", type(annotations))

                                print(annotations)
                                '''await curr.execute(
                                    """INSERT INTO training_data_annotations (user_id, image_name, training_img, annotations) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id, image_name) DO UPDATE SET annotations = training_data_annotations.annotations || EXCLUDED.annotations, updated_at=DEFAULT""",
                                    (user_id, image_name, training_img, annotations))
                                successful_inserts += len(annotations)'''
                                print("successful_inserts", successful_inserts)
                                image_name = None
                                training_img = None
                                annotations = None
                        return {'inserted_amount':successful_inserts}

                    except Exception:
                        logger.error("error inserting training_data", exc_info=True)


            except Exception:
                logger.error("error inserting training_data finding user email", exc_info=True)


async def get_postgres_training_recents(pool, session_user_email):
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            try:
                await curr.execute("SELECT id FROM users WHERE email = %s", (session_user_email,))
                user_row = await curr.fetchone()
                if user_row is None:
                    print("user not found, get_postgres_training_recents")
                    logger.info(("training recent get rejected, unknown user email ", session_user_email))
                    return None
                else:
                    user_id = user_row[0]
                    print("user_row all", user_row)

                    try:
                        await curr.execute("SELECT id,image_name,training_img,updated_at,annotations FROM training_data_annotations WHERE user_id = %s ORDER BY updated_at DESC", (user_id,))
                        await aconn.commit()
                        all_returned_from_db_sql = await curr.fetchall()
                        #print(all_returned_from_db_sql)
                        print("length of all_returned_from_db_sql",len(all_returned_from_db_sql))
                        #print("user recents data gotten")
                        return all_returned_from_db_sql

                    except Exception:
                        logger.error("error getting db training_data by user", exc_info=True)

            except Exception:
                logger.error("error getting recent training_datas find user by email", exc_info=True)


async def inserting_users_set_dataset_content(sendable,pool, session_user_email, dataset_name):
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            try:
                await curr.execute("SELECT id FROM users WHERE email = %s", (session_user_email,))
                user_row = await curr.fetchone()
                if user_row is None:
                    print("user not found, get_postgres_training_recents")
                    logger.info(("training recent get rejected, unknown user email ", session_user_email))
                    return None
                else:
                    user_id = user_row[0]
                    print("user_row all", user_row)

                    try:
                        print("getting dataset_name if exists", dataset_name," for ",user_id)
                        await curr.execute("SELECT user_id,name FROM datasets WHERE name = %s AND user_id = %s", (dataset_name,user_id,))

                        user_dataset_exists = await curr.fetchone()
                        print("user_dataset_exists??", user_dataset_exists)
                        if user_dataset_exists is None:
                            print("user_dataset_exists not found, inserting dataset")
                            try:
                                print("user found in db, inserting training data for ", user_id)
                                pic_id = None
                                image_name = None
                                training_img = None
                                annotations = None
                                successful_inserts = 0
                                contains_images = []
                                print("type of sendable", type(sendable))
                                print("length of sendable", len(sendable))
                                for i in sendable:
                                    print("type of i", type(i))
                                    # print(i)
                                    if i.get('id'):
                                        pic_id = i.get('id')
                                        print("id to insert", pic_id)
                                        contains_images.append(pic_id)
                                    if i.get('image_name'):
                                        image_name = i.get('image_name')
                                    if i.get('training_img'):
                                        training_img = i.get('training_img')
                                    if i.get('annotations'):
                                        annotations = i.get('annotations')

                                if pic_id is not None and image_name is not None and training_img is not None and annotations is not None:
                                    print("data to insert", len(contains_images), image_name, " ",
                                          len(training_img), " ", len(annotations))
                                    print("type of annotations", type(annotations))

                                    await curr.execute(
                                        """INSERT INTO datasets (user_id, contains_images, name) VALUES (%s, %s, %s) ON CONFLICT (name) DO UPDATE SET contains_images = datasets.contains_images || EXCLUDED.contains_images, updated_at=DEFAULT""",
                                        (user_id, contains_images, dataset_name))
                                    successful_inserts += len(contains_images)
                                    print("successful_inserts", successful_inserts)

                                return {'inserted_amount': successful_inserts}

                            except Exception:
                                logger.error("error inserting datasets contents in db", exc_info=True)

                        else:
                            logger.info(("user_dataset_exists in db for user, returning.. ", dataset_name, user_id))
                            return {'dataset_naming_error': 'dataset already exists'}
                    except Exception:
                        logger.error("error in searching datasets for user", exc_info=True)

            except Exception:
                logger.error("error getting recent training_datas find user by email", exc_info=True)

async def getting_proxy_metrics_for_groundtruth(pool, image_name):
    logger.info("in db getting_proxy_metrics_for_groundtruth")
    logger.info(pool.connection())
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            try:
                listofall_found_annotations_per_camera = []
                camera_index_pruned = image_name.find("/", 30)
                print("camera_index_pruned is", camera_index_pruned)
                camera_index_dot_removed = image_name.find(".", camera_index_pruned)
                print("camera_index_dot_removed is", camera_index_dot_removed)
                camera_searchable_name = image_name[camera_index_pruned + 1:camera_index_dot_removed]
                camera_searchable_name = camera_searchable_name[0:6]
                print("camera_searchable_name is", camera_searchable_name)
                try:
                    await curr.execute("SELECT name,near,municipality,latitude,longitude FROM cameras WHERE id = %s",
                                       (camera_searchable_name,))
                    first_cam_row_found = await curr.fetchone()
                    print("first_cam_row_found is", first_cam_row_found)
                    lat = first_cam_row_found[3]
                    lon = first_cam_row_found[4]
                    try:
                        await curr.execute(
                            """SELECT camera_id, camera_name, municipality, latitude, longitude, distance_km FROM find_cameras_within_distance(%s, %s, %s)""",
                            (lat, lon, 50))

                        nearby_cameras = await curr.fetchall()
                        logger.info(("nearby cameras per image", len(nearby_cameras)))

                        for camera in nearby_cameras:
                            # print(camera)
                            camera_url_name_to_match = f"%{camera[0]}%"
                            # löydetään kaikki camera id:t
                            # kunhan ne sisältävät kameran id numberon jossain kohtaa textissä
                            await curr.execute(
                                "SELECT id, updated_at, annotations FROM training_data_annotations WHERE image_name LIKE %s",
                                (camera_url_name_to_match,))
                            all_found_annotations_per_camera = await curr.fetchall()
                            if len(all_found_annotations_per_camera) > 0:
                                logger.info("found a matching camera id")
                                print(len(all_found_annotations_per_camera))
                                print(all_found_annotations_per_camera)
                                listofall_found_annotations_per_camera.append(all_found_annotations_per_camera)
                        logger.info("results of all found annotations for image")
                        print(len(listofall_found_annotations_per_camera))
                        print(listofall_found_annotations_per_camera)
                        return listofall_found_annotations_per_camera

                    except Exception:
                        logger.info("Found imagename but errored in latlon calculation")
                except Exception:
                    logger.info("tried to get image names lat and lon coordinates")
            except Exception:
                logger.error("error at start of getting proxy_metrics from db", exc_info=True)



async def inserting_locust_comparison_metrics(pool, insertable):
    async with pool.connection() as aconn:
        async with aconn.cursor() as curr:
            try:
                #hello
                successful_inserts = 0
                print("hello from db's side")
                await curr.execute(
                    """INSERT INTO metrics_locust_added_model_data (job_number_id, jobs_predict_id, classname_id, confidence_score, image_file_handling, 
                    preprocess_to_tensor, inference, bbox_and_segmask, original_img_encode, batchlist_creation, 
                    encode_images, redis, whole_runs_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    ON CONFLICT (job_number_id) DO UPDATE SET job_number_id=EXCLUDED.job_number_id, jobs_predict_id=EXCLUDED.jobs_predict_id,
                     classname_id = EXCLUDED.classname_id, confidence_score= EXCLUDED.confidence_score, image_file_handling=EXCLUDED.image_file_handling,
                     preprocess_to_tensor=EXCLUDED.preprocess_to_tensor, inference=EXCLUDED.inference, bbox_and_segmask=EXCLUDED.bbox_and_segmask, original_img_encode=EXCLUDED.original_img_encode,
                    batchlist_creation=EXCLUDED.batchlist_creation, encode_images=EXCLUDED.encode_images, redis=EXCLUDED.redis, whole_runs_time=EXCLUDED.whole_runs_time, created_at=DEFAULT""",
                    (insertable['job_id'], insertable['jobs_predict_id'], insertable['class_id'], insertable['confidence_score'],
                     insertable['image_file_handling'], insertable['preprocess_to_tensor'], insertable['inference'],
                     insertable['bbox_and_segmask'], insertable['original_img_encode'], insertable['batchlist_creation'],
                     insertable['encode_images'], insertable['redis'], insertable['whole_runs_time']))
                successful_inserts += 1
                print("successful_inserts", successful_inserts)
                return {'inserted_amount':successful_inserts}
            except Exception:
                logger.error("error inserting_locust_comparison_metrics by job", exc_info=True)
