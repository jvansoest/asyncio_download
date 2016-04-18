"""executor_download.py

Download from server.py with an asyncio executor.
"""

import requests
import asyncio
import time
import os.path
import os
from functools import partial


def gen_urls(start=0, per_page=5):
    more = True

    while more:
        data = {'start': start, 'per_page': per_page}
        resp = requests.post('http://localhost:5000/api/list_files', data=data)
        more = bool(resp.headers['More'].lower() == 'true')
        for url in resp.json()['urls']:
            yield url
            start += 1


def download(url, dest):
    resp = requests.get('http://localhost:5000/api/download/' + url)
    with open(os.path.join(dest, url), 'w') as f:
        f.write(resp.text)


def main():
    dest = "executor_results/{:.0f}".format(time.time())
    if not os.path.isdir(dest):
        os.makedirs(dest)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    tasks = []
    for url in gen_urls():
        func = partial(download, url, dest)
        tasks.append(loop.run_in_executor(None, func=func))
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

if __name__ == "__main__":
    main()
