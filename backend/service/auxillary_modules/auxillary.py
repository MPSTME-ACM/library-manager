'''Helper functions and decorators'''
from functools import wraps
from traceback import format_exc
from flask import request
from werkzeug.exceptions import BadRequest
import re

# Helper Methods
def validateDetails(number : str, email : str, emailRegex : str ="^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", **kwargs) -> bool:
    try:
        if not (len(number) == 10 and number.isnumeric()):
            return False
        if not re.fullmatch(emailRegex, email):
            return False
    except:
        return False
        

### Decorators ###
def enforce_JSON(endpoint):
    @wraps(endpoint)
    def decorated(*args, **kwargs):
        if request.mimetype.split("/")[-1].lower() != "json":
            raise BadRequest(f"{request.method} {request.root_path} expects JSON body")
        return endpoint(*args, **kwargs)
    return decorated

def silent_exec(method):
    @wraps(method)
    def decorated(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            print(f"Silencing exception, details: {e}\n.{format_exc()}")
    return decorated