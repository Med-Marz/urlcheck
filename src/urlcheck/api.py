import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException

from urlcheck.checker import check_urls
from urlcheck.models import CheckRequest, CheckResult

app = FastAPI(title="urlcheck")


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.environ.get("URLCHECK_API_KEY", "")
    if (
        expected == ""
        or x_api_key is None
        or not secrets.compare_digest(x_api_key, expected)
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post(
    "/check",
    response_model=list[CheckResult],
    dependencies=[Depends(require_api_key)],
)
async def check(request: CheckRequest) -> list[dict]:
    return await check_urls(request.urls)
