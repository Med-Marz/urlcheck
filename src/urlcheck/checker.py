import httpx

response = httpx.get("https://github.com")
print(response.status_code)