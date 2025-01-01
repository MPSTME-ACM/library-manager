from service import db
from sqlalchemy.types import INTEGER, SMALLINT, VARCHAR, BOOLEAN
from sqlalchemy.dialects.postgresql import DATE, TIME, TIMESTAMP
import datetime as dt

class QueuedParty(db.Model):
    __tablename__ = "queued_parties"
    
    id = db.Column(INTEGER, primary_key=True)

    holder_name = db.Column(VARCHAR(64), nullable=False)
    holder_phone = db.Column(SMALLINT, nullable=False, index=True)
    holder_email = db.Column(VARCHAR(64), nullable=False, index=True)

    time_booked = db.Column(TIMESTAMP, nullable=False)
    queued_index = db.Column(SMALLINT, nullable=False, default=0)

    room_id = db.Column(SMALLINT, nullable=False)
    slot_id = db.Column(INTEGER, db.ForeignKey("slots.id"), nullable=False)
    slot_time = db.Column(TIME, nullable=False)
    slot_date = db.Column(DATE, nullable=False)

    passkey = db.Column(VARCHAR(4), nullable = False)

    def __init__(self, hName : str, hPhone : str | int, hMail : str, tBooked : dt.datetime, index : int, room_id : int, slot_id : int, slot_time : dt.time, slot_date : dt.date, passkey : str):
        self.holder_name=hName
        self.holder_phone=hPhone
        self.holder_email=hMail
        self.time_booked=tBooked
        self.queued_index=index
        self.room_id=room_id
        self.slot_id=slot_id
        self.slot_time=slot_time
        self.slot_date=slot_date
        self.passkey=passkey

    def __repr__(self) -> str:
        return f"<QueuedParty({self.holder_name}, {self.holder_phone}, {self.holder_email}, {self.time_booked}, {self.queued_index}, {self.slot_id}, {self.slot_time}, {self.slot_date}) (DB ID: f{self.id}) object at f{id(self)}>"
    
    def __CustomDict__(self) -> dict:
        '''Return (JSON serializable) dict'''
        return {"name" : self.holder_name,
                "email" : self.holder_email,
                "phone" : self.holder_phone,
                "time_booked" : self.time_booked.strftime("%Y-%m-%d %H:%M"),
                "queue_index" : self.queued_index,
                "room_id" : self.room_id,
                "slot_date" : self.slot_date.strftime("%d%m%y"),
                "slot_time" : self.slot_time.strftime("%H%m")}
    
class Slot(db.Model):
    __tablename__ = "slots"

    id = db.Column(INTEGER, primary_key=True)

    time_slot = db.Column(TIME, nullable=False)
    date = db.Column(DATE, nullable=False)
    room = db.Column(SMALLINT, nullable=False)
    booked = db.Column(BOOLEAN, nullable=False, default=False)

    queue_length = db.Column(SMALLINT, nullable=False, default=0)

    holder = db.Column(INTEGER, nullable=True)

    def __init__(self, time : dt.time, date : dt.date, booked : bool, qLen : int, holder : int):
        self.time_slot = time,
        self.date = date,
        self.booked = booked
        self.queue_length = qLen
        self.holder = holder

    def __repr__(self) -> str:
        return f"<Slot({self.time_slot, self.date, self.booked, self.queue_length, self.holder})> (DB ID: {self.id}) at {id(self)}"

    def __CustomDict__(self) -> dict:
        '''Return (JSON serializable) dict'''
        return {"time" : self.time_slot.strftime("%H:%M"),
                "date" : self.date.strftime("%d%m%Y"),
                "booked" : self.booked,
                "qLen" : self.queue_length,
                "holder" : self.holder}