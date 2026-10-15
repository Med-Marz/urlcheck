FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir --prefix=/install .


FROM python:3.12-slim

RUN useradd --create-home --uid 1000 appuser

COPY --from=builder /install /usr/local

USER appuser
WORKDIR /home/appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn urlcheck.api:app --host 0.0.0.0 --port ${PORT:-8000}"]