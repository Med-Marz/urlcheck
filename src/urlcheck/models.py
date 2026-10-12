from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    url: str
    status: int | None
    error: str | None
    attempts: int
    seconds: float


class CheckRequest(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=100)
