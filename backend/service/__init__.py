from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from service.config import configObj

app = Flask(__name__)
app.config.from_object(configObj)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from service import models
from service import routes