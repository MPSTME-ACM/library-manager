from service import app, db
from backend.service.models import Slot

from flask import request, Response, jsonify
from werkzeug.exceptions import BadRequest, Conflict, NotFound, InternalServerError

from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime, timedelta, time

### ENDPOINTS ###
@app.route("/rooms/<int:id>/slots", methods=["GET"])
def getRoomDetails(id) -> Response:
    req_date = request.args.get("date")
    req_time = request.args.get("time")

    clauses = [Slot.room==id]
    currentDate = datetime.date(datetime.now())

    if not (req_date or req_time):
        clauses.append(Slot.date >= currentDate & Slot.date < currentDate + timedelta(days=app.config["FUTURE_WINDOW_SIZE"]))

    if req_time:
        try:
            req_time = int(req_time)
            if req_time < app.config["OPENING_TIME"] or req_time > app.config["CLOSING_TIME"]:
                raise ValueError()
            
            req_time = time(req_time // 100, 0)

            clauses.append(Slot.time == req_time)

        except ValueError:
            raise BadRequest(f"Time specified must be between {app.config['OPENING_TIME']} to {app.config['CLOSING_TIME']}, and be an integer")
    
    if req_date:
        try:
            req_date = datetime.strptime(req_date, "%d%m%y").date()
            if req_date > currentDate + timedelta(days=app.config["FUTURE_WINDOW_SIZE"]):
                raise BadRequest(f"You can only book rooms til {(currentDate + timedelta(days=app.config['FUTURE_WINDOW_SIZE'])).strftime('%d%m%y')}")
            
            clauses.append(Slot.date == req_date)

        except ValueError:
            e = BadRequest("Date must be formatted as `ddmmyy`, no alphabets or special characters allowed")
            e.__setattr__("additional_info", f"For example, today's date would be formatted as: {currentDate.strftime('%d%m%y')}")
            raise e
    
    try:
        results = db.session.execute(select(Slot).where(and_(*clauses))).scalars().all()
        if not results:
            return jsonify([]), 404
        
        pyReadableResult = [result.__CustomDict__() for result in results]
        return jsonify(pyReadableResult), 200
    except SQLAlchemyError as e:
        raise InternalServerError("There seems to be an issue with our database service, please try again later :(")
    except AttributeError:
        print("Invalid objects fetched, check Slot.__CustomDict__() and Slot schema")
        raise InternalServerError() #NOTE: Generic decriptions are handled by @app.errorhandler(InternalServerError), no need to set description manually

@app.route("/book/<int:id>", methods=["POST"])
def bookRoom() -> Response:
    ...

@app.route("/enqueue/<int:id>", methods=["POST"])
def enqueueToRoom() -> Response:
    ...

@app.route("/cancel/<int:id>", methods=["DELETE"])
def cancelBooking() -> Response:
    ...