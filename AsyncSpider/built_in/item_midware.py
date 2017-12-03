from ..base_classes import ItemMidware

__all__ = ['ItemCounter']


class ItemCounter(ItemMidware):
    def __init__(self):
        super().__init__()
        self.count = 0

    async def transport(self, *items):
        self.count += len(items)
        return items
