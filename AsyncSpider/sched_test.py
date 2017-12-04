import sched
import asyncio
import logging
import time
import os

class TestContext:
    def __init__(self):
        self.x = 0

    def initial_feed(self, scheduler):
        logging.info("[+] initial_feed called")
        logging.info("[*] Testing basic execution")

        scheduler.schedule(self.basic_exec)

    def basic_exec(self, scheduler):
        logging.info("[+] basic_exec OK")
        logging.info("[*] Testing async execution")

        scheduler.schedule(self.async_exec)

    async def async_exec(self, scheduler):
        start_time = time.time()
        await asyncio.sleep(0.1)
        end_time = time.time()
        elapsed = end_time - start_time

        if elapsed > 0.11 or elapsed < 0.09:
            raise Exception("Incorrect sleep time")

        logging.info("[+] async_exec OK")
        scheduler.schedule(self.parallel_exec)

    async def parallel_exec(self, scheduler):
        logging.info("[*] Testing parallel execution")

        logging.info("[*] (12, 1) ...")
        await self.parallel_exec_once(12, 1)

        logging.info("[*] (24, 2) ...")
        await self.parallel_exec_once(24, 2)

        logging.info("[+] parallel_exec OK")
        scheduler.schedule(self.success)

    def parallel_exec_once(self, n_exec, expected_timing):
        exec_ctx = {
            "n_done": 0
        }

        start_time = time.time()
        sleep_time = 0.1
        expected_duration = sleep_time * expected_timing

        fut = asyncio.Future()

        async def executor(scheduler):
            await asyncio.sleep(sleep_time)
            exec_ctx["n_done"] += 1
            n_done = exec_ctx["n_done"]
            if n_done == n_exec:
                await on_done()
            elif n_done > n_exec:
                raise Exception("n_done > n_exec")

        async def on_done():
            end_time = time.time()
            elapsed = end_time - start_time

            if elapsed > expected_duration * 1.1 or elapsed < expected_duration * 0.9:
                fut.set_exception(Exception("Incorrect sleep time: " + str(elapsed)))
            else:
                fut.set_result(None)

        for i in range(n_exec):
            scheduler.schedule(executor)

        return fut

    def success(self, scheduler):
        logging.info("[+] All tests passed")
        os._exit(0)

def on_test_timeout():
    logging.error("[!] Test timeout")
    os._exit(1)

logging.basicConfig(level = logging.INFO)

loop = asyncio.get_event_loop()
scheduler = sched.Scheduler(loop)
scheduler.run_workers(16)

ctx = TestContext()
scheduler.schedule(ctx.initial_feed)

loop.call_later(10, on_test_timeout)

loop.run_forever()
