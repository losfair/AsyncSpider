from AsyncSpider import *
import datetime

# ---params------------------------------------------------------

target_url = 'https://www.baidu.com/'
# target_url = 'https://www.hao123.com/'
total = 2000
max_concurrent_node_num = 2000
request_limit: int = None


# ----code-------------------------------------------------
class ReqNode(Node):
    async def main(self, spd: Spider):
        url = self.kwargs['url']
        try:
            resp = await spd.request('get', url, timeout=5)
            status = str(resp.status)
            spd.config['count'] += 1
        except (AioTimeoutError, AioCancelledError):
            status = 'failed'
        kp = dict(
            time=datetime.datetime.now(),
            count=str(self.kwargs['count']).rjust(len(str(total))),
            total=total,
            status=status.ljust(6),
            url=url
        )
        info = '{time}\t{count}/{total}\tstatus: {status}\turl: {url}'.format(**kp)
        await spd.save(info)


if __name__ == '__main__':
    components = {
        'fetcher': AioFetcher(),
        'saver': PrintSaver(),
        'node_queue': FifoNodeQueue(*[ReqNode(url=target_url, count=i + 1, total=total) for i in range(total)]),
        'request_midwares': [RequestLimiter(max_req_num_per_sec=request_limit), RequestCounter()],
        'config': {
            'count': 0
        }
    }

    spider = Spider(**components)

    spider.run(max_concurrent_node_num=max_concurrent_node_num)
    spider.close()

    p = [
        spider.config['count'],
        total,
        spider.run_time,
        round(spider.request_midwares[-1].req_per_second, 2)
    ]

    print('passed requests: {}\n'
          'total requests: {}\n'
          'total time: {}s\n'
          'send requests per second: {}'.format(*p))
