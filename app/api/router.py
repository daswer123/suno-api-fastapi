from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from app.models.suno_api import SunoAPI
from app.api.deps import get_suno_api
from app.schemas.schemas import (
    GenerateRequest, GenerateResponse,
    CustomGenerateRequest, GenerateResponse,
    GenerateLyricsRequest, GenerateLyricsResponse,
    ExtendAudioRequest, ExtendAudioResponse,
    ConcatAudioRequest,
    GetMusicResponse, GetLimitResponse, GetClipResponse,
)

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate_music(request: GenerateRequest, suno_api: SunoAPI = Depends(get_suno_api)):
    try:
        response = await suno_api.generate(
            request.prompt,
            request.make_instrumental,
            request.wait_audio,
        )
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/custom_generate", response_model=GenerateResponse)
async def custom_generate_music(request: CustomGenerateRequest, suno_api: SunoAPI = Depends(get_suno_api)):
    try:
        response = await suno_api.custom_generate(
            request.prompt,
            request.tags,
            request.title,
            request.make_instrumental,
            request.wait_audio,
        )
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_lyrics", response_model=GenerateLyricsResponse)
async def generate_lyrics(request: GenerateLyricsRequest, suno_api: SunoAPI = Depends(get_suno_api)):
    try:
        response = await suno_api.generate_lyrics(request.prompt)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get", response_model=GetMusicResponse)
async def get_music(ids: Optional[str] = None, suno_api: SunoAPI = Depends(get_suno_api)):
    try:
        song_ids = ids.split(",") if ids else None
        response = await suno_api.get(song_ids)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_limit", response_model=GetLimitResponse)
async def get_limit(suno_api: SunoAPI = Depends(get_suno_api)):
    try:
        response = await suno_api.get_credits()
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extend_audio", response_model=ExtendAudioResponse)
async def extend_audio(request: ExtendAudioRequest, suno_api: SunoAPI = Depends(get_suno_api)):
    try:
        response = await suno_api.extend_audio(
            request.audio_id,
            request.prompt,
            request.continue_at,
            request.tags,
            request.title,
        )
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/concat")
async def concat_audio(request: ConcatAudioRequest, suno_api: SunoAPI = Depends(get_suno_api)):
    try:
        response = await suno_api.concatenate(request.clip_id)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clip", response_model=GetClipResponse)
async def get_clip(clip_id: str, suno_api: SunoAPI = Depends(get_suno_api)):
    try:
        response = await suno_api.get_clip(clip_id)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
