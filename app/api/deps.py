from app.models.suno_api import SunoAPI

async def get_suno_api() -> SunoAPI:
    suno_api = SunoAPI()
    await suno_api.init()
    return suno_api
