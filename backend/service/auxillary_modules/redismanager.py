from redis import Redis
from redis.typing import ResponseT

from traceback import format_exc

class RedisManager:
    '''Interface for Redis protocol, suppresses all errors, everything else remains the same'''
    def __init__(self, host : str, port : int, **kwargs):
        self._interface = Redis(host, port, **kwargs)

    def safe_execute_command(self, command : str, returnBytes : bool = True, *args, **kwargs) -> ResponseT | bytes | None:
        try:
            _result : bytes | str | None = self._interface.execute_command(command, *args, **kwargs)
            if isinstance(_result, str) and returnBytes:
                return _result.decode('utf-8')
            return _result

        except Exception as e:
            print(f"Silencing exception raied in Redis execution, details: {e}\n.{format_exc()}")
            return None