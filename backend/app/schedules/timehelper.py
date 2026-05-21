import time
from backend.app.config import logger


def get_time() -> str:
    # hakee nykyisen ajan ja palauttaa sen str
    logger.info("in get_time", exc_info=True)
    return time.strftime('%X (%d/%m/%y)')