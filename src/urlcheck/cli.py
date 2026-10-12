import asyncio
import json
import sys
from urllib.parse import urlparse

from urlcheck.checker import check_urls


def read_urls(path):
    urls = []
    with open(path) as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def is_valid_url(text):
    parts = urlparse(text)
    return parts.scheme in ("http", "https") and parts.netloc != ""


def split_valid_urls(urls):
    valid = []
    invalid = []
    for url in urls:
        if is_valid_url(url):
            valid.append(url)
        else:
            invalid.append(url)
    return valid, invalid


async def run(path):
    urls = read_urls(path)
    valid, invalid = split_valid_urls(urls)
    for url in invalid:
        print(f"Skipping invalid URL: {url}", file=sys.stderr)
    return await check_urls(valid)


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/urlcheck/cli.py urls.txt", file=sys.stderr)
        sys.exit(2)
    results = asyncio.run(run(sys.argv[1]))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()