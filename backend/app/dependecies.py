import httpx
from . import settings

# client on saatavilla globalisti moneen saman hostin api requestiin, clientti tehdään vain kerran
# host on laitettuna settings obj (Settings()) /config.py tiedostosta joka saa tiedot .env
# kun appi sammutetaan (lifestate = yield) -> client nollataan
_client:httpx.AsyncClient
async def shared_client_start():
    global _client

    _client = httpx.AsyncClient(
        base_url=settings.digitraffic_base,
        timeout=httpx.Timeout(10.0, connect=5.0),
        headers={"Accept": "application/json"},
    )
    print("\n ..dependencies done: ", _client)
    return _client



async def shared_client_close() -> None:
    global _client
    await _client.aclose()
    _client = None

def get_shared_client() -> httpx.AsyncClient:
    return _client
