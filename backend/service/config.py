import os
from dotenv import load_dotenv

CWD = os.path.dirname(__file__)
print(CWD)


output = load_dotenv(dotenv_path=os.path.join(os.path.dirname(CWD), '.env'),
                verbose=True,
                override=True)

if not output:
    print(f"ERROR: Failed to parse .env file at: {os.path.join(os.path.dirname(CWD), '.env')}. Make sure path is entered correctly, and that a file actually exists there.")
    raise FileNotFoundError()

print(os.environ)

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

    except KeyError as e:
        print(f"ERROR: Missing configuration in {os.path.dirname(CWD), '.env'}, check .env file, Original Error: {e}")
        raise e
    except ValueError as e:
        print(f"ERROR: Invalid configuration in {os.path.dirname(CWD), '.env'}. Original Error: {e}")
        raise e
    
configObj = AppConfig()