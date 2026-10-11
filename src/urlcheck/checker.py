import asyncio
import time
import httpx


async def check_url(url):
    start = time.time()
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
            response = await client.get(url)
        status = response.status_code
        error = None
    except httpx.TimeoutException:
        status = None
        error = "timeout"
    except httpx.RequestError as exc:
        status = None
        error = type(exc).__name__
    end = time.time()
    return {
        "url": url,
        "status": status,
        "error": error,
        "seconds": round(end - start, 2),
    }


async def main():
    results = await asyncio.gather(
        check_url("https://github.com"),
        check_url("https://python.org"),
        check_url("https://wikipedia.org"),
        check_url("https://this-does-not-exist-12345.com"),
    )
    for result in results:
        print(result)


asyncio.run(main())