from .models import Node

__all__ = ['FifoNodeQueue', 'LifoNodeQueue']


class NodeQueueBaseClass:
    def __init__(self, *nodes):
        self._queue = []
        self.put(*nodes)

    @staticmethod
    def _check_node(obj):
        if not isinstance(obj, Node):
            raise TypeError('{} is not a Node instance.'.format(obj))

    def put(self, *nodes):
        raise NotImplementedError

    def get(self):
        try:
            return self._queue.pop(0)
        except IndexError:
            return None

    @property
    def is_empty(self):
        try:
            self._queue[0]
        except IndexError:
            return True
        else:
            return False

    def __len__(self):
        return self._queue.__len__()  # class FifoNodeQueue:


class FifoNodeQueue(NodeQueueBaseClass):
    def put(self, *nodes):
        for obj in nodes:
            self._check_node(obj)
            self._queue.append(obj)


class LifoNodeQueue(NodeQueueBaseClass):
    def put(self, *nodes):
        self._queue = list(nodes).extend(self._queue)
