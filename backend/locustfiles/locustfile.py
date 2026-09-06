import os
import uuid
os.environ["PSYCOPG_WAIT_FUNC"] = "wait_select"
import psycopg
import psycopg_pool
from locust import task,events, between, HttpUser
from locust.runners import MasterRunner
from testcontainers.community.postgres import PostgresContainer

from backend.app.config import logger, loggercrier
from backend.app.main import app

# a standalone psycopg connection for datatables initalization
# for load testing using Locust as this happens just once per run
def creating_sim_users_table(connection_info):
    #pool = sim_locust_pool
    with psycopg.connect(connection_info) as aconn:
        with aconn.cursor() as curr:
            try:
                logger.info("creating sim database table users..")

                curr.execute(
                    """ CREATE TABLE users (
                    id SERIAL NOT NULL,
                    username VARCHAR(20),
                    email VARCHAR(30) UNIQUE,
                    password VARCHAR
                    )""")


                aconn.commit()
                logger.info("sim db table created!")

            except psycopg.Error as e:
                if e.diag:
                    print(f"SQLSTATE Code: {e.diag.sqlstate}")
                    print(f"Primary Message: {e.diag.message_primary}")
                    print(f"Severity: {e.diag.severity}")
                    print(f"Table Name: {e.diag.table_name}")
                    print(f"Constraint Name: {e.diag.constraint_name}")
                    print(f"Column Name: {e.diag.column_name}")
                logger.error("error inserting user", exc_info=True)
                logger.error("error creating sim user db table", exc_info=True)


@events.init.add_listener
def using_database_TestContainer(environment, **kwargs):
    logger.info("staring locust load testing")
    if not isinstance(environment.runner, MasterRunner):
        print("Beginning test setup")
    else:
        print("Started test from Master node")
    logger.info(("enviroiment passed ", environment.stats))
    container = PostgresContainer("postgres:16-alpine")
    container.start()
    connection_info = (
        f"dbname={container.dbname} "f"user={container.username} "f"password={container.password} "f"host={container.get_container_host_ip()} "f"port={container.get_exposed_port(5432)}")

    creating_sim_users_table(connection_info)
    logger.info("creating_sim_users_table finished in init")

    # käytetään ConnectionPoolia simuloituun Locust trafficiin.
    sim_locust_pool = psycopg_pool.ConnectionPool(connection_info, open=False)

    sim_locust_pool.open()
    sim_locust_pool.wait()
    logger.info("app state contents")
    logger.info(app.state._state)
    app.state.pool = sim_locust_pool
    app.state.TestContainer = container
    logger.info(("sim_locust_pool connection ", sim_locust_pool.connection))
    logger.info(("staring locust load testing init ended, ", app.state.pool, " ", app.state.TestContainer))




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
        self.sim_username = uuid.uuid4()
        logger.info(("sim user created,",self.sim_username))

    @task(1)
    def creating_sim_user(self):
        logger.info("creating sim username")
        try:
            self.client.post("/auth/signup", json={'username':f"{self.sim_username}",'email': f"{self.sim_username}_sim_user@g.cm", 'password': '111111'})
        except Exception:
            logger.error("error inserting sim user at API call", exc_info=True)

    @task(2)
    def sim_user_signin(self):
        try:
            logger.info("login in sim username")
            response = self.client.post("/auth/signin", json={'username':f"{self.sim_username}",'email': f"{self.sim_username}_sim_user@g.cm", 'password': '111111'})
        except Exception:
            logger.error("error login in sim user at API call", exc_info=True)