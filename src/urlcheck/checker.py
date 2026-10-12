import asyncio
import time
import httpx


async def check_url(url, max_attempts=3, timeout=5.0):
    start = time.time()
    status = None
    error = None
    attempts = 0

    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
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


async def check_urls(urls, max_concurrent=10, timeout=5.0):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_check(url):
        async with semaphore:
            return await check_url(url, timeout=timeout)

    tasks = []
    for url in urls:
        tasks.append(limited_check(url))
    return await asyncio.gather(*tasks)


async def main():
    urls = [
        "https://github.com",
        "https://python.org",
        "https://wikipedia.org",
        "https://this-does-not-exist-12345.com",
    ]
    results = await check_urls(urls)
    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())