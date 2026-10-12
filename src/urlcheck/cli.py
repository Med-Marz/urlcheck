from urllib.parse import urlparse


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