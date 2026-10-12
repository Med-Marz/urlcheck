from fastapi import FastAPI

from urlcheck.checker import check_urls
from urlcheck.models import CheckRequest, CheckResult

app = FastAPI(title="urlcheck")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/check", response_model=list[CheckResult])
async def check(request: CheckRequest) -> list[dict]:
    return await check_urls(request.urls)
