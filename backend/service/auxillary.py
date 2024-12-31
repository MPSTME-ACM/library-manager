'''Helper functions and decorators'''
from functools import wraps
from flask import request, current_app
from werkzeug.exceptions import BadRequest

### Decorators ###
def enforce_JSON(endpoint):
    @wraps
    def decorated(*args, **kwargs):
        if request.mimetype.split("/")[-1].lower() != "json":
            raise BadRequest(f"{request.method} {request.root_path} expects JSON body")
        return endpoint(*args, **kwargs)
    return decorated