from .models import Request, Response, Item

__all__ = ['ComponentBaseClass',
           'FetcherBaseClass',
           'SaverBaseClass',
           'RequestMidware',
           'ItemMidware',
           ]


class ComponentBaseClass:
    def __init__(self):
        self.is_activated = False

    def activate(self):
        # need "super().activate()" when overrode
        if self.is_activated:
            raise RuntimeError('{} is already activated.'.format(self))
        else:
            self.is_activated = True

    def close(self):
        # need "super().close()" when overrode
        if self.is_activated:
            self.is_activated = False
        else:
            raise RuntimeError('close {} before activating it.'.format(self))


class FetcherBaseClass(ComponentBaseClass):
    async def request(self, request: Request) -> Response:
        raise NotImplementedError


class SaverBaseClass(ComponentBaseClass):
    async def save(self, *items):
        raise NotImplementedError


class MidwareBaseClass(ComponentBaseClass):
    async def transport(self, obj):
        raise NotImplementedError


class RequestMidware(MidwareBaseClass):
    async def transport(self, request: Request) -> Request:
        return request


class ItemMidware(MidwareBaseClass):
    async def transport(self, *items) -> (Item,):
        return items
