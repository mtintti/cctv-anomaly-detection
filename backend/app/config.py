from pydantic_settings import BaseSettings
import json
import logging.config
import logging.handlers
import pathlib
from backend.app.logger import JSONFormatter
# tallennettu Settings() luokkasta, täytetään __init__.py tiedostossa. Täällä on settings.kutsumanimet
class Settings(BaseSettings):
    digitraffic_base:str
    db_name:str
    db_user: str
    db_pass: str
    db_host: str
    db_port: str
    desktop: str
    desktop_ann: str
    outerfile: str
    segann: str

# loggin tiedot käyttäen. Config tiedosto (/logging_configs) laitetaan json muodossa logging:iin
# DEBUG, INFO, ja WARNING leveling viestit loggerista printatataan std:cout terminaliin
# ERROR ja CRITICAL virheet menevät cctv-detection.log tiedostoon (logging_configs/logs)
logger = logging.getLogger("cctv_detection")
loggercrier = logging.getLogger("cctv_detection_CriticAndErr")


def setup_Logging():
    parent_folder_structure = pathlib.Path(__file__).parent
    config_file_loc = parent_folder_structure / "logging_configs" / "config.json"
    with open(config_file_loc) as f_in:
        config = json.load(f_in)
        config["handlers"]["file"]["filename"] = str(parent_folder_structure / "logging_configs" / "logs" / "cctv-detection.log")
        config_file_loc.parent.mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(config)

def logmain():
    setup_Logging()
    # testi että virheet tulevat ohjelman alkaessa oikein :>
    '''logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    loggercrier.error("error message")
    loggercrier.critical("critical message")'''