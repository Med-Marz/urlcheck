import asyncio
import time
import httpx


async def check_url(url, max_attempts=3):
    start = time.time()
    status = None
    error = None
    attempts = 0

    async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
        for attempt in range(1, max_attempts + 1):
            attempts = attempt
            try:
                response = await client.get(url)
                status = response.status_code
                error = None
            except httpx.TimeoutException:
                status = None
                error = "timeout"
            except httpx.RequestError as exc:
                status = None
                error = type(exc).__name__

            failed = error is not None or (status is not None and status >= 500)
            if not failed or attempt == max_attempts:
                break

            await asyncio.sleep(2 ** (attempt - 1))

    end = time.time()
    return {
        "url": url,
        "status": status,
        "error": error,
        "attempts": attempts,
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


if __name__ == "__main__":
    asyncio.run(main())