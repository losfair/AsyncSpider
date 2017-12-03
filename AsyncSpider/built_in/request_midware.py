from ..base_classes import RequestMidware
from ..models import Request
import time
import asyncio

__all__ = ['RequestCounter', 'RequestLimiter']


class RequestCounter(RequestMidware):
    def __init__(self):
        super().__init__()
        self.count = 0
        self._t0 = None
        self._t1 = None

    @property
    def total_seconds(self):
        return round(self._t1 - self._t0, 6)

    @property
    def req_per_second(self):
        return self.count / self.total_seconds

    async def transport(self, request: Request) -> Request:
        self._t1 = time.time()
        if self._t0 is None:
            self._t0 = self._t1
        self.count += 1
        return request


class RequestLimiter(RequestMidware):
    def __init__(self, max_req_num_per_sec: int = None):
        super().__init__()
        self.max_req_num_per_sec = max_req_num_per_sec
        self._base_point = None
        self._req_queue = [0]

    async def transport(self, request: Request) -> Request:
        if self.max_req_num_per_sec is None:
            # disabled
            return request
        else:
            # enabled
            if self._base_point is None:
                self._base_point = time.time()
                self._req_queue[0] += 1
                return request
            else:
                # refresh base_point & req_queue
                now = time.time() - self._base_point
                _ = int(now)
                if _ >= 1:
                    self._base_point += _
                    if _ >= len(self._req_queue):
                        self._req_queue = [0]
                    else:
                        for __ in range(_):
                            self._req_queue.pop(0)

                # distribute interval
                for i, req_num in enumerate(self._req_queue):
                    if req_num < self.max_req_num_per_sec:
                        self._req_queue[i] += 1
                        target_time = i
                        break
                else:
                    target_time = len(self._req_queue)
                    self._req_queue.append(1)

                await asyncio.sleep(target_time - now)
                return request
