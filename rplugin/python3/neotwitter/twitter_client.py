import os
import webbrowser

import tweepy


class TwitterClient(object):
    """ A Twitter Client """

    def __init__(self, user):
        """ Client instance Constructor

        :param user: A sqlalchemy model """

        self.user = user
        self.consumer_key = os.environ.get('NEOTWITTER_API_KEY')
        self.consumer_secret = os.environ.get('NEOTWITTER_SECRET_KEY')
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)

    def get_authorization_url(self):
        """ Opens a browser page to the the url given by the Twitter API service
        return: True
        """
        try:
            redirect_url = self.auth.get_authorization_url()
        except tweepy.TweepError:
            return False
        return webbrowser.open_new_tab(redirect_url)  # This returns True

    def get_access_token(self, verifier):
        """ :param verifier: The verifier key from the Twitter API """
        try:
            access_token, access_secret = self.auth.get_access_token(verifier)
        except tweepy.TweepError:
            # Should also return a tuple if it fails
            return False, False
        return access_token, access_secret

    def _rebuild_auth(self, user):
        """
        Creates an instance of the Twitter OAuthHandler
        :param user: A sqlalchemy model
        :return: auth:
        """
        self.auth = tweepy.OAuthHandler(TwitterClient.consumer_key,
                                        TwitterClient.consumer_secret)
        self.auth.set_access_token(self.user.access_token,
                                   self.user.access_token_secret)
        return self.auth

    def build_api(self):
        """ build the Twitter client API
        :returns a new instance of the "OAuthHandler" which is ready for use
        """
        self.auth = self._rebuild_auth(self.user)
        return tweepy.API(self.auth)
