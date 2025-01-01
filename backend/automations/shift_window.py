import psycopg2 as pg
import os
from traceback import format_exc
from dotenv import load_dotenv
from datetime import datetime, time, timedelta

CWD = os.path.dirname(__file__)


output = load_dotenv(dotenv_path=os.path.join(os.path.dirname(CWD), '.env'),
                verbose=True)

if not output:
    raise FileNotFoundError(f".env file at {os.path.join(os.path.dirname(CWD), '.env')} not found. Script execution aborted. Time: {datetime.now()}")

DB_CONFIG_KWARGS = {
    "database" : os.environ["DB_NAME"],
    "user" : os.environ["DB_USERNAME"],
    "password" : os.environ["DB_PASSWORD"],
    "host" : os.environ["DB_URI"]
}

ROOMS = [1,2,3]

op_time = os.environ["LIB_OPENING_TIME"]
cl_time = os.environ["LIB_CLOSING_TIME"]

#NOTE: Not importing any modules here for the sake of simplicity.
try:
    open_hour = int(op_time[:2])
    close_hour = int(cl_time[:2])
except Exception as e:
    raise ValueError(f"Invalid time format. Ensure times are in HHMM format like '0700' and '1900'. Original Exception: {format_exc}")

# Validate the extracted hours
if not (0 <= open_hour <= 23) or not (0 <= close_hour <= 23):
    raise ValueError("Hours must be between 00 and 23.")

if open_hour >= close_hour:
    raise ValueError("Opening time must be earlier than closing time.")

new_date = (datetime.today() + timedelta(days=3)).date()

opening_time = datetime.combine(new_date, time(open_hour, 0))
closing_time = datetime.combine(new_date, time(close_hour, 0))

purge_date = (datetime.today() - timedelta(days=1)).date()

try:
    conn =  pg.connect(**DB_CONFIG_KWARGS)
    with conn.cursor() as db_cursor:
        for room_id in ROOMS:
            current_time = opening_time
            while current_time <= closing_time:
                db_cursor.execute("INSERT INTO SLOTS (room, date, time, booked, queue_length) VALUES (%s, %s, %s, %s, %s)", (room_id, new_date, current_time, False, 0,))
                current_time += timedelta(hours=1)

        conn.commit()

        db_cursor.execute("DELETE FROM SLOTS WHERE date < %s", (purge_date,))
        conn.commit()
        
    conn.close()

except:
    if conn:
        conn.rollback()
    print("ERROR: SCRIPT FAILED")
finally:
    if conn:
        conn.close()