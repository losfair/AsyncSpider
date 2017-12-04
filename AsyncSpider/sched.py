import asyncio
import logging

JOB_KIND_STOP = "stop"
JOB_KIND_RUN_EXECUTOR = "run_executor"

class Worker:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.running = False

    def start(self):
        if self.running:
            raise Exception("Attempting to start a worker that is already running")
        self.running = True
        self.scheduler.loop.create_task(self._run())

    async def _run(self):
        while True:
            job = await self.scheduler.job_queue.get()
            assert(isinstance(job, Job))

            if job.kind == JOB_KIND_STOP:
                await self.scheduler.job_queue.put(job)
                return
            elif job.kind == JOB_KIND_RUN_EXECUTOR:
                try:
                    maybe_coroutine = job.executor(self.scheduler)
                    if asyncio.iscoroutine(maybe_coroutine):
                        await maybe_coroutine
                except Exception as e:
                    logging.error(e)
            else:
                logging.error(Exception("Unknown job kind: " + job.kind))

class Job:
    def __init__(self, kind, executor = None):
        self.kind = kind
        self.executor = executor

class Scheduler:
    def __init__(self, loop = None):
        if loop == None:
            loop = asyncio.get_event_loop()

        self.loop = loop
        self.job_queue = asyncio.Queue() # [Job]
        self.leak_workers = False

    def __del__(self):
        if not self.leak_workers:
            self.job_queue.put_nowait(Job(JOB_KIND_STOP))

    def run_workers(self, n = 16):
        for i in range(n):
            worker = Worker(self)
            worker.start()

    # Prototype for `executor`: (Scheduler) -> None | coroutine
    def schedule(self, executor):
        self.job_queue.put_nowait(Job(JOB_KIND_RUN_EXECUTOR, executor))
