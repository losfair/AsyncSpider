from .models import Request, Response
from .base_classes import ComponentBaseClass
from collections import Iterable
import asyncio
import time

__all__ = ['Spider']


class Spider(ComponentBaseClass):
    def __init__(self, node_queue, fetcher, saver,
                 request_midwares: list = None,
                 item_midwares: list = None, config: dict = None):
        super().__init__()

        self.node_queue = node_queue
        self.fetcher = fetcher
        self.saver = saver
        self.request_midwares = request_midwares if request_midwares is not None else []
        self.item_midwares = item_midwares if item_midwares is not None else []
        self.config = config if config is not None else {}
        self.run_time = None

    def activate(self):
        super().activate()
        self.fetcher.activate()
        self.saver.activate()
        for x in self.request_midwares:
            x.activate()
        for x in self.item_midwares:
            x.activate()

    def close(self):
        super().__init__()
        self.fetcher.close()
        self.saver.close()
        for x in self.request_midwares:
            x.close()
        for x in self.item_midwares:
            x.close()

    def run(self, max_concurrent_node_num=10):
        t0 = time.time()
        if not self.is_activated:
            self.activate()

        work_num = [0]

        def get_nodes(num):
            nodes = []
            for _ in range(num):
                node = self.node_queue.get()
                if node is None:
                    break
                else:
                    nodes.append(node)
            return nodes

        async def manager():
            manager_lock = asyncio.Lock()

            async def work(node):
                try:
                    next_nodes = await node.main(self)
                finally:
                    work_num[0] -= 1
                    if manager_lock.locked():
                        manager_lock.release()
                if next_nodes is None:
                    pass
                elif isinstance(next_nodes, Iterable):
                    self.node_queue.put(tuple(next_nodes))
                else:
                    raise RuntimeError('{} returned an inappropriate object {}'.format(node, next_nodes))

            first_works = [work(node) for node in get_nodes(max_concurrent_node_num)]
            asyncio.ensure_future(asyncio.wait(first_works))
            work_num[0] += len(first_works)

            while True:
                await manager_lock.acquire()
                if work_num[0] == 0:
                    if self.node_queue.is_empty:
                        break
                    else:
                        new_nodes_num = max_concurrent_node_num
                elif work_num[0] < max_concurrent_node_num:
                    new_nodes_num = max_concurrent_node_num - work_num[0]
                elif work_num[0] == max_concurrent_node_num:
                    new_nodes_num = 0

                if new_nodes_num > 0:
                    new_nodes = get_nodes(new_nodes_num)
                    if new_nodes:
                        new_works = [work(node) for node in new_nodes]
                        asyncio.ensure_future(asyncio.wait(new_works))
                        work_num[0] += len(new_works)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(loop.create_task(manager()))
        self.run_time = round(time.time() - t0,6)

    async def request(self, method, url, timeout=10, params=None, headers=None, proxy=None, **kwargs) -> Response:
        req = Request(method, url, timeout, params, headers, proxy, **kwargs)
        for rmw in self.request_midwares:
            req = await rmw.transport(req)
        return await self.fetcher.request(req)

    async def save(self, *items):
        for imw in self.item_midwares:
            items = await imw.transport(*items)
        await self.saver.save(*items)
