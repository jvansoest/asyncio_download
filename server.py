"""server.py

Flask based mock server to test asyncio_download
"""

from flask import Flask, request, json, make_response, abort
import random
import time
import uuid

app = Flask(__name__)

# num_files = random.randint(20, 30)
num_files = 25
api_data = {'data': [{str(uuid.uuid4()).replace('-', ''): n}
                     for n in range(num_files)]}


def lag():
    """Add a slight random lag to responses"""
    return random.randint(0, 3) / 10
    # return 0

@app.route('/api/list_files', methods=['GET', 'POST'])
def list_files():
    if request.method == "GET":
        return json.jsonify(api_data)
    if request.method == "POST":
        start = int(request.values.get('start', 0))
        per_page = int(request.values.get('per_page', 3))
        per_page = min(per_page, 5)
        end = start + per_page

        time.sleep(lag())

        url_slice = api_data['data'][start:min(end, num_files)]
        urls = {'urls': [k for url in url_slice for k, v in url.items()]}
        response = json.jsonify(urls)
        response.headers['More'] = bool(end < num_files)
        return response


@app.route('/api/download/<target_file>')
def download_file(target_file):

    time.sleep(lag())

    try:
        num = next(url[target_file] for url in api_data['data']
                   if url.get(target_file) is not None)
    except StopIteration:
        abort(404)
    msg = "{} of {}".format(num + 1, num_files)
    response = make_response(msg)
    response.headers["Content-Disposition"] = ("attachment; filename={}.txt"
                                               .format(target_file))
    response.content_type = 'text/plain; charset=UTF-8'
    return response

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
