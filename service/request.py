from urllib.request import Request, urlopen
import json

# a service to performan http request to this rest api

BASE_HOST = 'localhost'
mutable_port = 5000 # mutable, so that to support custom port

def request(path: str, method='GET', data=None):
    if data:
        data = json.dumps(data).encode("utf-8")
    headers = {"Content-type": "application/json; charset=UTF-8"} \
                if data else {}

    path = path if path.startswith('/') else f'/{path}'
    req = Request(url=f'http://{BASE_HOST}:{mutable_port}{path}', data=data, headers=headers, method=method)
    with urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result


def post(path, data={}):
    return request(path, 'POST', data)

def put(path, data ={}):
    return request(path, 'PUT', data)

# get request no need payload
def get(path):
    return request(path)

def delete(path):
    return request(path, 'DELETE')



