import asyncio
import random
from typing import Optional

async def sleep(x: float, y: Optional[float] = None) -> None:
    timeout = random.uniform(x, y) if y is not None and y != x else x
    await asyncio.sleep(timeout)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}
