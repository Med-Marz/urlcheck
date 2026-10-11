import time
import httpx


def check_url(url):
    start = time.time()
    response = httpx.get(url, follow_redirects=True, timeout=5.0)
    end = time.time()
    return {
        "url": url,
        "status": response.status_code,
        "seconds": round(end - start, 2),
    }


print(check_url("https://github.com"))
print(check_url("https://python.org"))