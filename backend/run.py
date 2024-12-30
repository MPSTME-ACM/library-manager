'''Test file for running the app. Development only, not for production'''

from service import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host=app.config["HOST"], port=app.config["PORT"])