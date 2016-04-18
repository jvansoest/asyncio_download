# asyncio_download.py

Asyncio examples and
comparisons, purely for my learning and benefit.

## Introduction

I'm pretty new to [asyncio](https://docs.python.org/3/library/asyncio.html).
One use case that I encounter somewhat frequently is scraping / downloading a
large number of URLs -- asyncio seems like it could speed that up considerably.
I decided that perhaps the best way for me to learn (without burning through a
ton of API calls) would be to write a quick Flask app to act as an example
server.

### `asyncio_examples.ipynb`

A [Jupyter Notebook](http://jupyter.org/) of me comparing a number of the
different `asyncio` components and coroutines to help me understand the
differences between e.g. `asyncio.gather` and `asyncio.as_completed`, or
`asyncio.ensure_future` and `asyncio.wait`.

### `server.py`

A common pattern I've found is needing to call one URL to get a list of
(unpredictable) sub-URLs that are my actual target. Often, the first URL is
paginated, and in some cases there's no good way to tell how many pages to
expect. Instead, I tend to write a generator that simply checks for some
element that indicates there are more pages and `yield`s until that element
goes away, and I iterate over that generator to get the target URLs.

`server.py` tries to emulate this situation. For debugging purposes, you can
`GET` `/api/list_files` to see that it hosts 25 unique and unpredictable
endpoints. The content of each endpoint is a simple `x of 25`, where `x` is a
number from 1 to 25. This facilitates checking that all 25 endpoints were hit
once and only once. The default of 25 can be configured by changing
`num_files`.

The "API" returns a JSON response including a list of up to 5 of the endpoints
when a `POST` request is sent to `api/list_files`, and like many such paginated
APIs, it accepts parameters `start` and `per_page` (max 5). The response
headers include a `More` key indicating whether there are remaining results
(`true`) or if the results have been exhausted (`false`).

### `verify_results.py`

Simple utility that takes a single argument -- a directory including the
downloaded files -- and verifies that each endpoint was hit and there are no
duplicates. By default the scripts download results to a timestamped
subdirectory of a appropriately named directory, e.g.
`executor_results/1461016940/`, so a few ways to verify the results look
correct include:

- `sort -n dir/subdir/*`
- `python3 verify_results.py dir/subdir`

### `download.py`

A standard synchronous script using
[`requests`](http://docs.python-requests.org/en/master/), for comparison. More
or less the way I probably would have accomplished the task in the past.

### `asyncio_download.py`

Asynchronous script using
`asyncio` and [`aiohttp`](http://aiohttp.readthedocs.org/en/stable/). Most
challenging part was finding the most efficient was to come up with an
asynchronous replacement for the generator that iterates until the `More`
header is `false`. What I've come up with is a little clunky, but
works.

### `executor_download.py`

Asynchronous script using `asyncio` and `requests` in an
[`Executor`](https://docs.python.org/3/library/asyncio-eventloop.html#executor).
While this may have some performance disadvantage in certain scenarios, it
seems to fare well in these tests, and was *much* simpler to write -- something
I'll definitely keep in mind when whipping up quick scripts.

## Results

On my 2015 Macbook Air (2.2 GHz Intel Core i7, 8 GB 1600 MHz DDR3)

- `num_files`: 25
    - Synchronous, requests
    - `python3 -m timeit -s 'from download import main' 'main()'`
        - 0 lag
            - `10 loops, best of 3: 228 msec per loop`
        - 0.3s lag
            - `10 loops, best of 3: 9.43 sec per loop`
    - Asynchronous (aiohttp)
    - `python3 -m timeit -s 'from asyncio_download import main' 'main()'`
        - 0 lag
            - `10 loops, best of 3: 188 msec per loop`
        - 0.3s lag
            - `10 loops, best of 3: 1.93 sec per loop`
    - Asynchronous (executor, requests)
    - `python3 -m timeit -s 'from executor_download import main' 'main()'`
        - 0 lag
            - `10 loops, best of 3: 213 msec per loop`
        - 0.3s lag
            - `10 loops, best of 3: 1.99 sec per loop`
