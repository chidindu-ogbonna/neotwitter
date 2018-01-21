import os
import webbrowser

import tweepy

from neotwitter.database import User, session
from neotwitter.utils import (get_request_token_from_db,
                              store_access_token_in_db,
                              store_request_token_in_db)


class TwitterClient(object):
    """ A Twitter Client """

    CONSUMER_KEY = os.environ.get('NEOTWITTER_API_KEY')
    CONSUMER_SECRET = os.environ.get('NEOTWITTER_SECRET_KEY')

    def __init__(self):
        self.user = session.query(User).first()
        self.auth = tweepy.OAuthHandler(self.CONSUMER_KEY,
                                        self.CONSUMER_SECRET)

    def get_authorization(self):
        """:returns: a tuple (boolean, status_message) """
        try:
            redirect_url = self.auth.get_authorization_url()
        except tweepy.TweepError as e:
            raise tweepy.TweepError('{}'.format(e))
            #  return False, '{}'.format(e)
        store_request_token_in_db(self.auth.request_token)
        # Evaluates to True
        return webbrowser.open_new_tab(redirect_url)

    def get_tokens(self, verifier):
        """:param verifier: g:neotwitter_verifier
        :returns: a boolean """
        try:
            self.auth.request_token = get_request_token_from_db()
            access_token = self.auth.get_access_token(verifier)
        except tweepy.TweepError as e:
            return False
        store_access_token_in_db(access_token)
        return True

    def _rebuild_auth(self):
        self.auth = tweepy.OAuthHandler(self.CONSUMER_KEY,
                                        self.CONSUMER_SECRET)
        self.auth.set_access_token(self.user.access_token,
                                   self.user.access_token_secret)
        return self.auth

    def build_api(self):
        auth = self._rebuild_auth()
        return tweepy.API(auth)
