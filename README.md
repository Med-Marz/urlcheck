# urlcheck

A small tool that checks whether websites respond. It reads a list of URLs, checks them concurrently, retries temporary failures, and prints a JSON report.

## Install

Requires Python 3.11 or newer.

```bash
git clone https://github.com/Med-Marz/urlcheck.git
cd urlcheck
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Put one URL per line in a text file. Blank lines and lines starting with `#` are ignored. Lines that are not valid http/https URLs are skipped with a message.

```bash
urlcheck urls.txt
urlcheck urls.txt --output report.json
urlcheck urls.txt --timeout 10 --concurrency 5
```

Each result looks like this:

```json
{
  "url": "https://python.org",
  "status": 200,
  "error": null,
  "attempts": 1,
  "seconds": 0.58
}
```

- `status` is the HTTP status code, or `null` if no answer was received.
- `error` is `"timeout"` or a connection error name, or `null`.
- `attempts` is how many tries the check needed (maximum 3).

A summary line is printed to the error output.

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | All URLs succeeded |
| 1 | At least one URL failed |
| 2 | Wrong usage |

A check counts as failed on a timeout, a connection error, or a status of 400 or higher.

## Configuration

| Option | Environment variable | Default |
| --- | --- | --- |
| `--timeout` | `URLCHECK_TIMEOUT` | 5 (seconds per request) |
| `--concurrency` | `URLCHECK_CONCURRENCY` | 10 (simultaneous checks) |

A command line flag wins over the environment variable.

## API

Start the server with a key:

```bash
URLCHECK_API_KEY=your-key uvicorn urlcheck.api:app
```

- `GET /health` returns `{"status": "ok"}` and needs no key.
- `POST /check` takes `{"urls": [...]}` (1 to 100 URLs) and needs an `X-API-Key` header matching `URLCHECK_API_KEY`. Without a valid key it returns 401. If the server has no key configured, every request is refused.

```bash
curl -X POST http://127.0.0.1:8000/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"urls": ["https://python.org"]}'
```

## Retry behavior

Timeouts, connection errors and server errors (status 500 and above) are retried up to 3 attempts, waiting about 1 s, then 2 s, each plus a small random delay. Other responses, such as 403 or 404, are not retried.

## Development

```bash
pytest
ruff check .
ruff format --check .
```

Tests use a fake web server, so they run offline.