from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from redis import Redis

from service.config import configObj
from service.auxillary_modules.redismanager import RedisManager

app = Flask(__name__)
app.config.from_object(configObj)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

try:
    redisManager = RedisManager(app.config["REDIS_HOST"], app.config["REDIS_PORT"])
except Exception as e:
    if app.config["REQUIRE_REDIS"]:
        raise ConnectionError("REQUIRE_REDIS set to True, but encountered failure in establishing connection to Redis")
    else:
        print("\n\n============== WARNING: RUNNING APP WITHOUT REDIS LAYER ==============\n\n")
        redisManager = None

from service import models
from service import routes