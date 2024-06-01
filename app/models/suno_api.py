import os
import httpx
from typing import List, Optional
from app.utils.utils import sleep

class SunoAPI:
    BASE_URL: str = "https://studio-api.suno.ai"
    CLERK_BASE_URL: str = "https://clerk.suno.com"

    def __init__(self):
        cookie_str = os.getenv("SUNO_COOKIE")
        if not cookie_str:
            raise Exception("SUNO_COOKIE is not set in environment variables")

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Cookie": cookie_str,
            },
        )
        self.sid: Optional[str] = None
        self.current_token: Optional[str] = None

    async def init(self):
        await self.get_auth_token()
        await self.keep_alive()
        return self

    async def get_auth_token(self):
        get_session_url = f"{self.CLERK_BASE_URL}/v1/client?_clerk_js_version=4.73.2"
        response = await self.client.get(get_session_url)
        data = response.json()
        if not data["response"]["last_active_session_id"]:
            raise Exception("Failed to get session id, you may need to update the SUNO_COOKIE")
        self.sid = data["response"]["last_active_session_id"]

    async def keep_alive(self, is_wait: bool = False):
        if not self.sid:
            raise Exception("Session ID is not set. Cannot renew token.")
        renew_url = f"{self.CLERK_BASE_URL}/v1/client/sessions/{self.sid}/tokens?_clerk_js_version==4.73.2"
        response = await self.client.post(renew_url)
        new_token = response.json()["jwt"]
        self.current_token = new_token
        self.client.headers["Authorization"] = f"Bearer {self.current_token}"
        if is_wait:
            await sleep(1, 2)

    async def generate(
        self,
        prompt: str,
        make_instrumental: bool = False,
        wait_audio: bool = False,
    ):
        await self.keep_alive()
        payload = {
            "make_instrumental": make_instrumental,
            "mv": "chirp-v3-5",
            "prompt": "",
            "gpt_description_prompt": prompt,
        }
        return await self._generate(payload, wait_audio)

    async def custom_generate(
        self,
        prompt: str,
        tags: str,
        title: str,
        make_instrumental: bool = False,
        wait_audio: bool = False,
    ):
        await self.keep_alive()
        payload = {
            "make_instrumental": make_instrumental,
            "mv": "chirp-v3-5",
            "prompt": prompt,
            "tags": tags,
            "title": title,
        }
        return await self._generate(payload, wait_audio)

    async def _generate(self, payload: dict, wait_audio: bool):
            response = await self.client.post("/api/generate/v2/", json=payload)
            data = response.json()

            if "clips" not in data:
                raise Exception(f"Unexpected response from Suno API: {data}")

            song_ids = [audio["id"] for audio in data["clips"]]

            if wait_audio:
                while True:
                    response = await self.get(song_ids)
                    all_completed = all(
                        audio["status"] in ["streaming", "complete"] for audio in response
                    )
                    if all_completed:
                        return response
                    await sleep(3, 6)
            else:
                return data["clips"]


    async def generate_lyrics(self, prompt: str):
        await self.keep_alive()
        response = await self.client.post("/api/generate/lyrics/", json={"prompt": prompt})
        data = response.json()
        generate_id = data["id"]
        while True:
            response = await self.client.get(f"/api/generate/lyrics/{generate_id}")
            data = response.json()
            if data["status"] == "complete":
                if "text" not in data:
                    raise Exception(f"Unexpected response from Suno API: {data}")
                return {
                    "text": data["text"],
                    "title": data["title"],
                    "status": data["status"]
                }
            await sleep(2)



    async def extend_audio(
        self,
        audio_id: str,
        prompt: str = "",
        continue_at: str = "0",
        tags: str = "",
        title: str = ""
):  
        await self.keep_alive()
        payload = {
            "continue_clip_id": audio_id,
            "continue_at": continue_at,
            "mv": "chirp-v3-5",
            "prompt": prompt,
            "tags": tags,
            "title": title,
        }
        response = await self.client.post("/api/generate/v2/", json=payload)
        data = response.json()
        if "detail" in data:
            raise Exception(f"Error from Suno API: {data['detail']}")
        return data


    async def concatenate(self, clip_id: str):
        await self.keep_alive()
        payload = {"clip_id": clip_id}
        response = await self.client.post("/api/generate/concat/v2/", json=payload)
        data = response.json()
        if "detail" in data:
            raise Exception(f"Error from Suno API: {data['detail']}")
        return data

    async def get(self, song_ids: Optional[List[str]] = None):
        await self.keep_alive()
        url = "/api/feed/"
        if song_ids:
            url += f"?ids={','.join(song_ids)}"
        response = await self.client.get(url)
        return response.json()

    async def get_clip(self, clip_id: str):
        await self.keep_alive()
        response = await self.client.get(f"/api/clip/{clip_id}")
        return response.json()

    async def get_credits(self):
        await self.keep_alive()
        response = await self.client.get("/api/billing/info/")
        data = response.json()
        return {
            "credits_left": data["total_credits_left"],
            "period": data["period"],
            "monthly_limit": data["monthly_limit"],
            "monthly_usage": data["monthly_usage"],
        }
