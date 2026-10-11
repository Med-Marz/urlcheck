import asyncio
import time
import httpx


async def check_url(url):
    start = time.time()
    async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
        response = await client.get(url)
    end = time.time()
    return {
        "url": url,
        "status": response.status_code,
        "seconds": round(end - start, 2),
    }


async def main():
    print(await check_url("https://github.com"))
    print(await check_url("https://python.org"))


asyncio.run(main())