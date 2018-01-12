import os

import pyscreenshot
from sqlalchemy.exc import IntegrityError

from neotwitter.database import User, session


def user_in_db():
    """
    Check if a user exists in the database model

    :returns: a boolean
    """
    user = session.query(User).first()
    # Neccessary so the application does not move about with a Nonetype
    if not user:
        return False
    # Check if the access_token and access_token_secret exists in the database
    if user.access_token and user.access_token_secret:
        return True
    return False


def take_screenshot():
    """
    Take screenshot using the pyscreenshot module

    :returns: str (location to the screenshot file)
    """
    screenshot_file = '/tmp/screenshot.png'
    try:
        os.remove(screenshot_file)
    except FileNotFoundError:
        pass
    img = pyscreenshot.grab(bbox=(20, 20, 510, 510))
    img.save(screenshot_file)
    return screenshot_file


def get_request_token_from_db():
    """
    Get the request_token stored in the database

    :returns: str (request_token) or a negative boolean (if it does not exist)
    """
    user = session.query(User).first()
    if not user:
        return False
    return user.request_token


def store_request_token_in_db(request_token):
    """
    Store a request_token in the database

    :param :request_token A python dict
    :returns: a boolean
    """
    try:
        user = User(request_token=request_token)
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
    except:
        return False
    return True


def store_access_token_in_db(access_token):
    """
    Store the access_token key and access_token secret in the database

    :param :access_token a tuple (key, secret)
    :returns: a boolean
    """
    try:
        user = session.query(User).first()
        user.access_token = access_token[0]
        user.access_token_secret = access_token[1]
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
    except:
        return False
    return True
