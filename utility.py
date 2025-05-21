from flask import session, redirect, make_response, jsonify
from functools import wraps


def logged_in(f):
    @wraps(f)
    def inner(*args,  **kwargs):
        user = session.get("user")
        if user is None:
            return redirect("/login")
        else:
            return f(*args,  **kwargs)
    return inner


def apology(body, code=404):
    response = jsonify(body)
    response.status_code = code
    return response