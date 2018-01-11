import os

import pyscreenshot
from sqlalchemy.exc import IntegrityError

from neotwitter.database import User, session


def user_in_db():
    user = session.query(User).first()
    # check if user exists, neccessary so the application does not go around
    # throughing "Nonetype" errors
    if not user:
        return False
    # Check if the access_token and access_token_secret exists already
    if user.access_token and user.access_token_secret:
        return True
    return False


def take_screenshot():
    screenshot_location = '/tmp/screenshot.png'
    try:
        os.remove(screenshot_location)
    except FileNotFoundError:
        pass
    img = pyscreenshot.grab(bbox=(20, 20, 510, 510))
    img.save(screenshot_location)
    return screenshot_location


def get_request_token_from_db():
    user = session.query(User).first()
    if not user:
        return False
    return user.request_token


def store_request_token_in_db(request_token):
    """ :param :request_token A python dict """
    try:
        user = User(request_token=request_token)
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
    except:
        return False
    return True


def store_access_token_in_db(access_token, access_token_secret):
    try:
        user = session.query(User).first()
        user.access_token = access_token
        user.access_token_secret = access_token_secret
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
    except:
        return False
    return True
