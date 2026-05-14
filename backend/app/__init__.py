import os
from os import getenv

import dotenv
from dotenv import load_dotenv
from backend.app.config import Settings
# Config.py tiedoston obj settings() täytetään .evn tiedostosta
print(os.getenv((dotenv.find_dotenv("DIGITRAFFIC_BASE"))))
load_dotenv()
settings = Settings()