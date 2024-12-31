from service import app, db, redisManager
from service.models import Slot, QueuedParty
from backend.service.auxillary_modules.auxillary import enforce_JSON

from flask import request, Response, jsonify, abort
from werkzeug.exceptions import BadRequest, Conflict, NotFound, InternalServerError

from sqlalchemy import select, update, and_
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime, timedelta, time
import orjson

### ERROR HANDLERS ###
@app.errorhandler(BadRequest)
def err_badReq(e : BadRequest):
    body = {"message" : e.description}
    if hasattr(e, "additional_info"):
        body["info"] = e.additional_info
    return jsonify(body), 400

@app.errorhandler(InternalServerError)
@app.errorhandler(SQLAlchemyError)
@app.errorhandler(Exception)
def err_generic(e : Exception):
    body = {"message" : e.description}
    if hasattr(e, "additional_info"):
        body["info"] = e.additional_info
    return jsonify(body), 500
    

### ENDPOINTS ###
@app.route("/rooms/<int:id>/slots", methods=["GET"])
def getRoomDetails(id) -> Response:
    req_date = request.args.get("date")
    req_time = request.args.get("time")

    try:
        _result : bytes | None = redisManager.safe_execute_command("GET", True, f"{id}:{req_date}:{req_time}")
        if _result:
            return jsonify(orjson.loads(_result)), 200
    except Exception as e:
        print("Failed cache lookup")

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
        redisManager.safe_execute_command("SETEX", True, f"{id}:{req_date}:{req_time}", 300, orjson.dumps(pyReadableResult))
        return jsonify(pyReadableResult), 200
    except SQLAlchemyError as e:
        raise InternalServerError("There seems to be an issue with our database service, please try again later :(")
    except AttributeError:
        print("Invalid objects fetched, check Slot.__CustomDict__() and Slot schema")
        raise InternalServerError() #NOTE: Generic decriptions are handled by @app.errorhandler(InternalServerError), no need to set description manually

@app.route("/book/<int:id>", methods=["POST"])
@enforce_JSON
def bookRoom(id) -> Response:
    bookingData = request.get_json(force=True, silent=False)

    try:
        booking_date = bookingData["date"]
        booking_time = bookingData["time"]
        holder_num = bookingData["number"]
        holder_email = bookingData["email"]
        holder_name = bookingData["name"]

        booking_time = int(booking_time)
        if booking_time < app.config["OPENING_TIME"] or booking_time > app.config["CLOSING_TIME"]:
            raise ValueError()
                
        booking_time = time(booking_time // 100, 0)

        currentDate = datetime.date(datetime.now())
        booking_date = datetime.strptime(booking_date, "%d%m%y").date()
        if booking_date > currentDate + timedelta(days=app.config["FUTURE_WINDOW_SIZE"]):
            raise BadRequest(f"You can only book rooms til {(currentDate + timedelta(days=app.config['FUTURE_WINDOW_SIZE'])).strftime('%d%m%y')}")

    except KeyError as e:
        raise BadRequest(f"Mandatory field missing in JSON body of request sent to {request.root_path}")
    except ValueError as e:
        raise BadRequest(f"Invalid data sent to POST {request.root_path}")
    
    try:
        with db.session.begin():
            slot : Slot | None = db.session.execute(select(Slot)
                                            .where(Slot.room == id, Slot.booked == False, Slot.date == booking_date, Slot.time == booking_time)
                                            .with_for_update(nowait=True)
                                            ).scalar_one_or_none()

            if not slot:
                return jsonify("Slot Unavailable"), 404

            db.session.execute(update(Slot)
                               .where(Slot.id == slot.id)
                               .values(booked=True, 
                                       queue_length=1,
                                       holder=holder_email))

            newParty = QueuedParty(holder_name, holder_num, holder_email, datetime.now(), 0, slot.room, slot.id, slot.time, slot.date)
            db.session.add(newParty)

            db.session.commit()
            db.session.close()

            return jsonify({"room_id" : slot.room, "slot_time" : slot.time_slot, "slot_date" : slot.date}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error occurred while booking slot: {e}")
        abort(500)

@app.route("/enqueue/<int:id>", methods=["POST"])
def enqueueToRoom() -> Response:
    bookingData = request.get_json(force=True, silent=False)

    try:
        booking_date = bookingData["date"]
        booking_time = bookingData["time"]
        holder_num = bookingData["number"]
        holder_email = bookingData["email"]
        holder_name = bookingData["name"]

        booking_time = int(booking_time)
        if booking_time < app.config["OPENING_TIME"] or booking_time > app.config["CLOSING_TIME"]:
            raise ValueError()
                
        booking_time = time(booking_time // 100, 0)

        currentDate = datetime.date(datetime.now())
        booking_date = datetime.strptime(booking_date, "%d%m%y").date()
        if booking_date > currentDate + timedelta(days=app.config["FUTURE_WINDOW_SIZE"]):
            raise BadRequest(f"You can only book rooms til {(currentDate + timedelta(days=app.config['FUTURE_WINDOW_SIZE'])).strftime('%d%m%y')}")

    except KeyError as e:
        raise BadRequest(f"Mandatory field missing in JSON body of request sent to {request.root_path}")
    except ValueError as e:
        raise BadRequest(f"Invalid data sent to POST {request.root_path}")
    
    try:
        with db.session.begin():
            slot : Slot | None = db.session.execute(select(Slot)
                                            .where(Slot.room == id, Slot.booked == True, Slot.date == booking_date, Slot.time == booking_time)
                                            .with_for_update(nowait=True)
                                            ).scalar_one_or_none()

            if not slot:
                return jsonify("Slot Unavailable"), 404
            
            if slot.queue_length >= app.config["MAX_QLEN"]:
                return jsonify(f"Queue length exceeds maximum allowed parties, which is {app.config['MAX_QLEN']}"), 422

            db.session.execute(update(Slot)
                            .where(Slot.id == slot.id)
                            .values(queue_length=slot.queue_length+1,
                                    holder=holder_email))

            newParty = QueuedParty(holder_name, holder_num, holder_email, datetime.now(), slot.queue_length+1, slot.room, slot.id, slot.time, slot.date)
            db.session.add(newParty)

            db.session.commit()
            db.session.close()

            return jsonify({"room_id" : slot.room, "slot_time" : slot.time_slot, "slot_date" : slot.date, "queue_index" : slot.queue_length + 1}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error occurred while booking slot: {e}")
        abort(500)

@app.route("/cancel/<int:id>", methods=["DELETE"])
def cancelBooking() -> Response:
    ...