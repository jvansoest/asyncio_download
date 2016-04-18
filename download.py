"""download.py

Download from server.py without asyncio
"""

import requests
import time
import os.path
import os


def gen_urls(start=0, per_page=5):
    more = True

    while more:
        data = {'start': start, 'per_page': per_page}
        resp = requests.post('http://localhost:5000/api/list_files', data=data)
        more = bool(resp.headers['More'].lower() == 'true')
        for url in resp.json()['urls']:
            yield url
            start += 1


def main():
    dest = "results/{:.0f}".format(time.time())
    if not os.path.isdir(dest):
        os.makedirs(dest)
    for url in gen_urls():
        resp = requests.get('http://localhost:5000/api/download/' + url)
        with open(os.path.join(dest, url), 'w') as f:
            f.write(resp.text)


if __name__ == "__main__":
    main()
