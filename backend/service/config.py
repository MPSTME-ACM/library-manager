import os
from dotenv import load_dotenv
import redis

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

        OPENIING_TIME = int(os.environ["LIB_OPENING_TIME"])
        CLOSING_TIME = int(os.environ["LIB_CLOSING_TIME"])
        FUTURE_WINDOW_SIZE = int(os.environ["LIB_FUTURE_WINDOW_SIZE"])
        MAX_QLEN = int(os.environ["LIB_MAX_QUEUE_SIZE"])

    except KeyError as e:
        print(f"ERROR: Missing configuration in {os.path.dirname(CWD), '.env'}, check .env file, Original Error: {e}")
        raise e
    except ValueError as e:
        print(f"ERROR: Invalid configuration in {os.path.dirname(CWD), '.env'}. Original Error: {e}")
        raise e
    
configObj = AppConfig()