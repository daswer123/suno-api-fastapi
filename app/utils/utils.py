import asyncio
import random
from typing import Optional

async def sleep(x: float, y: Optional[float] = None) -> None:
    if y is not None and y != x:
        min_val = min(x, y)
        max_val = max(x, y)
        timeout = asyncio.to_thread(lambda: random.uniform(min_val, max_val))
    else:
        timeout = x
    await asyncio.sleep(timeout)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}
