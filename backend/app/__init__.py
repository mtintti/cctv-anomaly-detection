import os
from os import getenv

import dotenv
from dotenv import load_dotenv
from ..app.config import Settings
# Config.py tiedoston obj settings() täytetään .evn tiedostosta
load_dotenv()
settings = Settings()