from ..base_classes import SaverBaseClass
import os
import asyncio
import aiofiles

__all__ = ['NullSaver',
           'PrintSaver',
           'ListSaver',
           'TextSaver',
           'AioTextSaver',
           ]


class NullSaver(SaverBaseClass):
    async def save(self, *items):
        pass


class PrintSaver(SaverBaseClass):
    async def save(self, *items):
        for item in items:
            print(item)


class ListSaver(SaverBaseClass):
    def __init__(self):
        super().__init__()
        self.item_list = None

    def activate(self):
        super().activate()
        self.item_list = []

    def close(self):
        super().close()
        self.item_list = None

    async def save(self, *items):
        for item in items:
            self.item_list.append(item.obj)


class TextSaver(SaverBaseClass):
    def __init__(self, file_path, encoding='utf8', clear_existing_file=False):
        super().__init__()
        self.file_path = file_path
        self.encoding = encoding
        self.clear_existing_file = clear_existing_file
        self._file_stream = None

    def activate(self):
        super().activate()
        if self.clear_existing_file or not os.path.exists(self.file_path):
            open(self.file_path, 'w').close()
        self._file_stream = open(self.file_path, 'a', encoding='utf8')

    def close(self):
        super().close()
        self._file_stream.close()
        self._file_stream = None

    async def save(self, *items):
        for item in items:
            self.write_line(item.obj)

    def write_line(self, text: str):
        self._file_stream.write(text + '\n')


class AioTextSaver(SaverBaseClass):
    def __init__(self, file_path, encoding='utf8', clear_existing_file=False):
        super().__init__()
        self.file_path = file_path
        self.encoding = encoding
        self.clear_existing_file = clear_existing_file
        self._aiofile = None

    def activate(self):
        super().activate()
        if self.clear_existing_file or not os.path.exists(self.file_path):
            open(self.file_path, 'w').close()

        loop = asyncio.get_event_loop()

        async def _get_aiofile():
            return await aiofiles.open(self.file_path, mode='a', encoding=self.encoding)

        self._aiofile = loop.run_until_complete(loop.create_task(_get_aiofile()))

    def close(self):
        super().close()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(self._aiofile.flush(), self._aiofile.close()))

    async def save(self, *items):
        text_lines = (item.obj for item in items)
        tasks = [self.write_line(text) for text in text_lines]
        asyncio.ensure_future(asyncio.wait(tasks))

    async def write_line(self, text: str):
        await self._aiofile.write(text + '\n')
