from service import db
from sqlalchemy.types import INTEGER, SMALLINT, VARCHAR, DATETIME, BOOLEAN, TIME
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class QueuedParty(db.Model):
    __tablename__ = "queued_parties"
    
    id = db.Column(INTEGER, primary_key=True)

    holder_name = db.Column(VARCHAR(64), nullable=False)
    holder_phone = db.Column(SMALLINT, nullable=False, index=True)
    holder_email = db.Column(VARCHAR(64), nullable=False, index=True)

    time_booked = db.Column(DATETIME, nullable=False)
    queued_index = db.Column(SMALLINT, nullable=False, default=0)

    slot_id = db.Column(SMALLINT, db.ForeignKey("slots.id"), nullable=False)
    slot_time = db.Column(DATETIME, db.ForeignKey("slots.time"), nullable=False)

    def __init__(self, hName : str, hPhone : str | int, hMail : str, tBooked : datetime, index : int, slot_id : int, slot_time : datetime):
        self.holder_name = hName
        self.holder_phone=hPhone
        self.holder_email = hMail
        self.time_booked=tBooked
        self.queued_index=index
        self.slot_id=slot_id
        self.slot_time=slot_time

    def __repr__(self) -> str:
        return f"<QueuedParty({self.holder_name}, {self.holder_phone}, {self.holder_email}, {self.time_booked}, {self.queued_index}, {self.slot_id}, {self.slot_time}) (DB ID: f{self.id}) object at f{id(self)}>"
    
    def __CustomDict__(self) -> dict:
        '''Return (JSON serializable) dict'''
        return {"name" : self.holder_name,
                "email" : self.holder_email,
                "phone" : self.holder_phone,
                "time_booked" : self.time_booked.strftime("%Y-%m-%d %H:%M:%S"),
                "queue_index" : self.queued_index,
                "slot_id" : self.slot_id,
                "slot_time" : self.slot_time}
    
class Slot(db.Model):
    __tablename__ = "slots"

    id = db.Column(INTEGER, primary_key=True)

    time = db.Column(DATETIME, nullable=False)
    booked = db.Column(BOOLEAN, nullable=False, default=False)

    queue_length = db.Column(SMALLINT, nullable=False, default=0)

    holder = db.Column(INTEGER, db.ForeignKey("queued_parties.email"), nullable=False)

    def __init__(self, time : datetime, booked : bool, qLen : int, holder : int):
        self.time = time
        self.booked = booked
        self.queue_length = qLen
        self.holder = holder

    def __CustomDict__(self) -> dict:
        '''Return (JSON serializable) dict'''
        return {"time" : self.time.strftime("%Y-%m-%d %H:%M:%S"),
                "booked" : self.booked,
                "qLen" : self.queue_length,
                "holder" : self.holder}