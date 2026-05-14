from pydantic_settings import BaseSettings
# tallennettu Settings() luokkasta, täytetään __init__.py tiedostossa. Täällä on settings.kutsumanimet
class Settings(BaseSettings):
    digitraffic_base:str