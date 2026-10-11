import time
import httpx


def check_url(url):
    start = time.time()
    response = httpx.get(url)
    end = time.time()
    return response.status_code, end - start


print(check_url("https://github.com"))
print(check_url("https://python.org"))