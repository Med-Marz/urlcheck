from fastapi import FastAPI

app = FastAPI(title="urlcheck")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
