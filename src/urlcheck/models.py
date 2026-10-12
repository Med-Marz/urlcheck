from pydantic import BaseModel


class CheckResult(BaseModel):
    url: str
    status: int | None
    error: str | None
    attempts: int
    seconds: float
