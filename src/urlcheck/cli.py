import argparse
import asyncio
import json
import os
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


async def run(path, timeout=5.0, max_concurrent=10):
    urls = read_urls(path)
    valid, invalid = split_valid_urls(urls)
    for url in invalid:
        print(f"Skipping invalid URL: {url}", file=sys.stderr)
    return await check_urls(valid, max_concurrent=max_concurrent, timeout=timeout)


def summarize(results):
    total = len(results)
    succeeded = 0
    total_seconds = 0
    for result in results:
        total_seconds += result["seconds"]
        if (
            result["error"] is None
            and result["status"] is not None
            and result["status"] < 400
        ):
            succeeded += 1
    average = round(total_seconds / total, 2) if total > 0 else 0
    return {
        "total": total,
        "succeeded": succeeded,
        "failed": total - succeeded,
        "average_seconds": average,
    }


def exit_code(summary):
    if summary["failed"] > 0:
        return 1
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="urlcheck", description="Check whether websites respond."
    )
    parser.add_argument("file", help="text file with one URL per line")
    parser.add_argument("--output", help="save the JSON report to this file")
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.environ.get("URLCHECK_TIMEOUT", "5.0")),
        help="seconds to wait per request (env: URLCHECK_TIMEOUT, default 5)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=int(os.environ.get("URLCHECK_CONCURRENCY", "10")),
        help="maximum simultaneous checks (env: URLCHECK_CONCURRENCY, default 10)",
    )
    return parser


def main():
    args = build_parser().parse_args()

    results = asyncio.run(
        run(args.file, timeout=args.timeout, max_concurrent=args.concurrency)
    )
    report = json.dumps(results, indent=2)

    if args.output:
        with open(args.output, "w") as out:
            out.write(report)
        print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(report)

    summary = summarize(results)
    print(
        f"Checked {summary['total']}: {summary['succeeded']} ok, "
        f"{summary['failed']} failed, average {summary['average_seconds']} s",
        file=sys.stderr,
    )
    sys.exit(exit_code(summary))


if __name__ == "__main__":
    main()
