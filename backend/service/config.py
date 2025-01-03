import os, sys
from dotenv import load_dotenv
from auxillary_modules.redismanager import RedisManager

from typing import Any

CWD = os.path.dirname(__file__)


output = load_dotenv(dotenv_path=os.path.join(os.path.dirname(CWD), '.env'),
                verbose=True,
                override=True)

if not output:
    print(f"ERROR: Failed to parse .env file at: {os.path.join(os.path.dirname(CWD), '.env')}. Make sure path is entered correctly, and that a file actually exists there.")
    raise FileNotFoundError()

class AppConfig:
    try:
        SECRET_KEY = os.environ["APP_SECRET_KEY"]

        PORT = int(os.environ["APP_PORT"])
        HOST = os.environ["APP_HOST"]

        SQLALCHEMY_DATABASE_URI = "postgresql://{user}:{password}@{url}/{db}".format(user=os.environ["DB_USERNAME"],
                                                                                     password=os.environ["DB_PASSWORD"],
                                                                                     url=os.environ["DB_URI"],
                                                                                     db=os.environ["DB_NAME"])
        SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("DB_TRACK_MODIFICATIONS", False)

        REQUIRE_REDIS = bool(int(os.environ["REQUIRE_REDIS"]))
        REDIS_HOST = os.environ.get("REDIS_HOST")
        REDIS_PORT = int(os.environ.get("REDIS_PORT"))

        if REQUIRE_REDIS and not (REDIS_HOST and REDIS_PORT):
            raise ValueError("REQUIRE_REDIS set to True, but mandatory args not found")

        OPENING_TIME = int(os.environ["LIB_OPENING_TIME"])
        CLOSING_TIME = int(os.environ["LIB_CLOSING_TIME"])
        FUTURE_WINDOW_SIZE = int(os.environ["LIB_FUTURE_WINDOW_SIZE"])
        MAX_QLEN = int(os.environ["LIB_MAX_QUEUE_SIZE"])

    except KeyError as e:
        print(f"ERROR: Missing configuration in {os.path.dirname(CWD), '.env'}, check .env file, Original Error: {e}")
        raise e
    except ValueError as e:
        print(f"ERROR: Invalid configuration in {os.path.dirname(CWD), '.env'}. Original Error: {e}")
        raise e
    
class CacheManager(RedisManager):
    '''This class seems so useless but hey less network calls at least'''
    def __init__(self, maxSize : int, maxKeySize: int, maxValSize : int, host : str, port : int, **options):
        self._nanoCache : dict = {}
        self.maxSize = maxSize
        self.maxKeySize = maxKeySize
        self.maxValSize = maxValSize
        super().__init__(host, port, **options)

    def getSpaceData(self) -> str:
        return f"Mmeory occupied: {sys.getsizeof(self._nanoCache)}\nEntries{len(self._nanoCache)}"
    
    def addToCache(self, key : str, value : Any) -> str | None:
        if sys.getsizeof(self._nanoCache) > self.maxSize:
            print("Permissible memory exhausted, insertion denied")
            return
        
        if sys.getsizeof(value) > self.maxValSize:
            raise ValueError("Value exceeds maximum permissible size")
        
        if sys.getsizeof(key) > self.maxKeySize:
            raise ValueError("Key exceeds maximum permissible size")
        
        self._nanoCache[key] = value
        if sys.getsizeof(self._nanoCache) > self.maxSize:
            raise MemoryError("Permissible memory exhausted, future insertions will now be denied")
    
    def popFromCache(self, key) -> Any:
        return self._nanoCache.pop(key, None)

    def clearCache(self) -> None:
        self._nanoCache = {}

    def checkExistence(self, key) -> bool:
        # return self._nanoCache.get(key)
        return key in self._nanoCache          # peak example of Python "programming"
            
    def updateConstraints(self, **kwargs) -> None:
        '''Update memory contraints of _nanoCache.
        
        params: Same as constructor, just without the Redis signature and additional kwargs
        '''

        self.maxSize = kwargs.get("maxSize", self.maxSize)
        self.maxKeySize = kwargs.get("maxKeySize", self.maxKeySize)
        self.maxValSize = kwargs.get("maxValSize", self.maxValSize)


    def persistToFile(self) -> None:
        ...
        
    
configObj = AppConfig()