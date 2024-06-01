import os
from fastapi import FastAPI, Depends
from app.api.router import router as api_router
from app.models.suno_api import SunoAPI

def create_app():
    app = FastAPI(
        title="Suno API",
        description="Use API to call the music generation AI of suno.ai",
        version="0.1.0",
    )

    suno_api = None

    @app.on_event("startup")
    async def startup_event():
        nonlocal suno_api
        try:
            # cookie = os.environ.get("SUNO_COOKIE")
            suno_api = SunoAPI()
            await suno_api.init()
        except Exception as e:
            print(f"Failed to initialize SunoAPI: {str(e)}")
            raise e

    async def get_suno_api() -> SunoAPI:
        if suno_api is None:
            raise Exception("SunoAPI is not initialized")
        return suno_api

    app.include_router(api_router, prefix="/api", dependencies=[Depends(get_suno_api)])

    @app.get("/")
    async def root():
        return {"message": "Welcome to Suno API!"}

    return app
