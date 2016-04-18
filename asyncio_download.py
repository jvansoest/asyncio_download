"""asyncio_download.py

Download from server.py with aiohttp
"""

import asyncio
import aiohttp
import os
import time


async def list_files(s, start=0, per_page=5):
    data = {'start': start, 'per_page': per_page}
    list_url = 'http://localhost:5000/api/list_files'
    async with s.post(list_url, data=data) as resp:
        more = bool(resp.headers['More'].lower() == 'true')
        json = await resp.json()
        urls = json['urls']
        return urls, more


async def download(s, url, dest):
    download_url = 'http://localhost:5000/api/download/' + url
    async with s.get(download_url) as resp:
        with open(os.path.join(dest, url), 'wb') as f:
            while True:
                chunk = await resp.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)


async def run(s, dest, start=0):
    urls, more = await list_files(s, start=start)
    while True:
        coros = [download(s, url, dest) for url in urls]
        if more:
            start += len(urls)
            coros.append(list_files(s, start=start))
            results = await asyncio.gather(*coros)
            urls, more = results[-1]
        else:
            await asyncio.gather(*coros)
            break


def main():
    dest = "async_results/{:.0f}".format(time.time())
    if not os.path.isdir(dest):
        os.makedirs(dest)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    with aiohttp.ClientSession() as s:
        loop.run_until_complete(run(s, dest))
    loop.close()


if __name__ == "__main__":
    main()
