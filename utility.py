from flask import session, redirect, make_response, jsonify
from functools import wraps
import logging


def logged_in(f):
    @wraps(f)
    def inner(*args,  **kwargs):
        user = session.get("user")
        if user is None:
            return redirect("/login")
        else:
            return f(*args,  **kwargs)
    return inner


# Defaults to success
def notify(body={}, code=200):
    response = jsonify(
        {"status": "success", "text": "Operation successful!", **body}
    )
    response.status_code = code
    return response


def get_logger():
    logger = logging.getLogger("isolated")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    file_handler = logging.FileHandler("logfile.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(message)s - %(asctime)s')
    # file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger