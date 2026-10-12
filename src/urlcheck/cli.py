def read_urls(path):
    urls = []
    with open(path) as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            urls.append(line)
    return urls