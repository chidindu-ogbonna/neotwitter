import os
from datetime import datetime

import pyscreenshot
from sqlalchemy.exc import IntegrityError

#   make the fnction calling these not neccesarily need to know the particular
#   db to work on
from neotwitter.database import Tweets, User, session


def is_access_token_in_db(access_token):
    """
    Check if an "access_token" has been stored in db
    Returns: True if so, False Otherwise
    """
    if session.query(User).filter_by(access_token=access_token).first():
        return True
    return False


def is_a_user_in_db():
    """
    Check if there is a User in the db
    Returns: True if so, False Otherwise
    """
    if session.query(User).first():
        return True
    return False


def take_screenshot():
    """
    Takes the screenshot of the text editor
    Requires "pillow" and "scrot" are installed
    """
    screenshot_location = '/tmp/screenshot.png'
    try:
        os.remove(screenshot_location)
    except FileNotFoundError:
        pass
    img = pyscreenshot.grab(bbox=(20, 20, 510, 510))
    img.save(screenshot_location)
    return screenshot_location


def is_first_tweet():
    """
    Return True if this is the first tweet, False otherwise
    """
    tweets = session.query(Tweets).all()
    if len(tweets) <= 1:
        return True
    return False


def is_a_week_since_last_tweet():
    """
    Check if the duration between today and the last tweet is seven days old
    Returns True if its a week, False otherwise.
    """
    tweets = session.query(Tweets).all()
    last_tweet = tweets[-1].tweet_date
    todays_date = datetime.utcnow()

    last_tweet_date_in_the_month = int(last_tweet.strftime('%d'))
    todays_date_in_the_month = int(todays_date.strftime('%d'))

    difference = abs(todays_date_in_the_month - last_tweet_date_in_the_month)
    #  TODO: This will fail for different kind of dates, get a better date checking process <23-12-17, Chidindu Ogbonna> #
    # Using the idea that the difference betweens weeks regardless of the
    # months is 7 or 24
    if difference == 7 or difference == 24:
        return True
    else:
        return False


def store_access_token_in_db(access_token, access_token_secret):
    """
    Takes the access_token and access_token_secret stores them in the database
    Returns: True if successful and False otherwise.
    """
    try:
        user = User(
            access_token=access_token, access_token_secret=access_token_secret)
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
    except:
        return False
    return True
