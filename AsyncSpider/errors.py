from concurrent.futures import TimeoutError as AioTimeoutError
from concurrent.futures import CancelledError as AioCancelledError

__all__ = ['AioTimeoutError', 'AioCancelledError']
