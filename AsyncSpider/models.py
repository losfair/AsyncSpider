import json

__all__ = ['Node',
           'Item',
           'Request',
           'Response',
           ]


class Node:
    def __init__(self, **kwargs):
        self.kwargs = dict(**kwargs)

    async def main(self, spd):
        pass


class Item:
    def __init__(self, obj, **kwargs):
        self.obj = obj
        self.kwargs = dict(**kwargs)


class Request:
    def __init__(self, method, url, timeout=10, params=None, headers=None, proxy=None, **kwargs):
        self.method = method
        self.url = url
        self.timeout = timeout

        self.params = params
        self.headers = headers
        self.proxy = proxy

        self.kwargs = dict(**kwargs)
        self.kwargs.update(dict(params=params, headers=headers, proxy=proxy))


class Response:
    def __init__(self, request: Request, status: int, content: bytes, text: str):
        self.request = request
        self.status = status
        self.content = content
        self.text = text

    def json(self, **kwargs):
        return json.loads(self.content, **kwargs)
