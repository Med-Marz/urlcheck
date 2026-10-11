import time
import httpx

start = time.time()
response = httpx.get("https://github.com")
end = time.time()

print(response.status_code)
print(end - start)