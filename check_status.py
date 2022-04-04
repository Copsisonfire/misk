import time
import asyncio
import aiohttp
from typing import Optional

from .config import *

__all__ = []

_AIOHTTP_CLIENT_TIMEOUT = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)


async def check_status():
    async with aiohttp.ClientSession(timeout=_AIOHTTP_CLIENT_TIMEOUT) as session:
        while True:
            request_start: float = time.time()
            async with session.get(f'{ADMIN_PANEL_URL}api/bot/bot_users/{BOT_USER_ID}/', headers={"Authorization": f'Bearer {ADMIN_PANEL_TOKEN}'},
                                   timeout=_AIOHTTP_CLIENT_TIMEOUT) as response:
                request_end: float = time.time()
                if response.status != 200:
                    raise Exception('Not expected answer', {'code': response.status})
                try:
                    r = await response.json()
                except Exception as e:
                    print(e)
                    raise Exception("Can't get json")
                request_timestamp: Optional[float] = r.get("result", {}).get("store", {}).get("user_vars",
                                                                                    {}).get(LAST_REQUEST_TIMESTAMP_KEY)
                response_timestamp: Optional[float] = r.get("result", {}).get("store", {}).get("user_vars",
                                                                                    {}).get(LAST_RESPONSE_TIMESTAMP_KEY)
                if isinstance(request_timestamp and response_timestamp, float):
                    if (request_start - max(request_timestamp, response_timestamp)) > NO_MESSAGE_TIME_LIMIT:
                        if request_timestamp > response_timestamp:
                            bot_status: str = "Fail with white bot"
                        else:
                            bot_status: str = "Fail with grey bot"
                    else:
                        bot_status: str = "Ok"
                else:
                    raise Exception("Timestamps isn't float type")
                response_delay: float = request_end - request_start
            try:
                yield (bot_status, response_delay)
            except NameError:
                print("Haven't response")
            await asyncio.sleep(CHECK_INTERVAL - response_delay)

async def check():
    async for i in check_status():
        async with aiohttp.ClientSession(timeout=_AIOHTTP_CLIENT_TIMEOUT) as session:
            async with session.get(f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage',
                                   params={"chat_id": ADDRESS_USER_ID, "text": str(i)}) as resp:
                if resp.status != 200:
                    raise Exception('Failed tg_api request', {'code': resp.status})