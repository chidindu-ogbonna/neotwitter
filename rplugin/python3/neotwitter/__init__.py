import os

import neovim

from neotwitter.database import Base, User, engine, session
from neotwitter.twitter_client import TwitterClient, tweepy
from neotwitter.utils import (is_a_user_in_db, is_a_week_since_last_tweet,
                              is_first_tweet, store_access_token_in_db,
                              take_screenshot)


@neovim.plugin
class NeoTwitter(object):

    file_name = '/tmp/tweet.twitter'

    VARIABLE = 'neotwitter_verifier'
    CHAR_LENGTH = 140
    COLORSCHEME_MESSAGE = 'I am using "{}" colorscheme for the week. #Neovim #Vim #NeoTwitter'
    FILETYPE = 'twitter'
    EXT = 'twitter'

    def __init__(self, nvim):
        self.nvim = nvim
        Base.metadata.create_all(engine)

        user = session.query(User).first()
        self.twitter_client = TwitterClient(user)

    def get_access(self):
        if not self.twitter_client.get_authorization_url():
            return False
        else:
            return True

    def get_tokens(self, verifier):
        """:param verifier: Verifier from twitter API"""
        access_token, access_secret = self.twitter_client.get_access_token(verifier)
        if access_token:
            return store_access_token_in_db(access_token, access_secret)
        return False

    @neovim.command("TwitterStartSetup", sync=True)
    def neo_twitter_start_setup(self):
        if self.nvim.vars.get(NeoTwitter.VARIABLE):
            self.nvim.out_write('[NeoTwitter] Verifier has already been set, run TwitterCompleteSetup to continue setup \n')
        else:
            if self.get_access():
                self.nvim.out_write(
                    '[NeoTwitter] Please check your browser and save your "verifier" \n'
                )
            else:
                self.nvim.out_write('[NeoTwitter] Not able to start setup \n')

    @neovim.command("TwitterCompleteSetup", sync=True)
    def neo_twitter_complete_setup(self):
        verifier = self.nvim.vars.get(NeoTwitter.VARIABLE)
        if verifier and self.get_tokens(verifier):
            self.nvim.out_write('[NeoTwitter] Setup was successful \n')
        #  elif not self.get_tokens():
        #      self.nvim.out_write('[NeoTwitter] Not getting access tokens \n')
        elif not verifier:
            self.nvim.out_write('[NeoTwitter] Verifier has not been set \n')
        elif is_a_user_in_db():
            self.nvim.out_write('[NeoTwitter] A User record already exists \n')
        else:
            self.nvim.out_write('[NeoTwitter] Not able to complete setup \n')

    @neovim.command("TweetColorscheme")
    def tweet_colorscheme(self):
        """
        tweet_colorscheme():
        Tweets the colorscheme used by vim once a week
        """
        auth = self.twitter_client.build_api()
        colorscheme = self.nvim.vars.get('colors_name')
        message = NeoTwitter.COLORSCHEME_MESSAGE.format(colorscheme)
        if is_first_tweet():
            #  TODO:  <01-01-18, Chidindu Ogbonna> # 
            # Add the functionality of saving in db after tweeting
            try:
                auth.update_with_media(take_screenshot(), status=message)
                self.nvim.out_write(
                    '[NeoTwitter: Your first tweet] Tweeted colorscheme is "{}" \n'.
                    format(colorscheme))
            except tweepy.TweepError as e:
                self.nvim.out_write('[NeoTwitter] Error: {} \n'.format(e))
        elif is_a_week_since_last_tweet():
            try:
                auth.update_with_media(take_screenshot(), status=message)
                self.nvim.out_write(
                    '[NeoTwitter] Tweeted colorscheme is "{}" \n'.format(
                        colorscheme))
            except tweepy.TweepError as e:
                self.nvim.out_write('[NeoTwitter] Error: {} \n'.format(e))

    @neovim.command("TweetCompose")
    def compose_tweet(self):
        self._set_twitter_buffer()
        self.nvim.out_write(
            '[NeoTwitter] Note: If longer than 140 characters, your tweet would be reduced to 140, use "TweetCheckCharacterLength" to check the length \n'
        )

    @neovim.command("TweetCheckCharacterLength", sync=True)
    def check_length(self):
        buffer_content = self.nvim.current.buffer[:]
        length = len('. '.join(buffer_content))
        self.nvim.out_write('Tweet Length is {} \n'.format(length))

    @neovim.command("TweetPost")
    def post_tweet(self):
        """
        Post the content of the buffer, if the length of characters is
        greater than 140, it trims it.
        """
        buffer_ = self.nvim.current.buffer
        # Check if the buffer name includes "twitter"
        if buffer_.name.split('.')[-1] == NeoTwitter.FILETYPE:
            tweet = self._trim_buffer()
            try:
                auth = self.twitter_client.build_api()
                auth.update_status(tweet)
                self.nvim.out_write('[NeoTwitter] Your tweet was sent \n')
            except tweepy.TweepError as e:
                self.nvim.out_write('[NeoTwitter] Error: {} \n'.format(e))
            except Exception as e:
                self.nvim.out_write('[NeoTwitter] Error: {} \n'.format(e))
        else:
            self.nvim.out_write('This is not a tweet file \n')

    @neovim.autocmd('BufEnter', pattern='*.twitter', eval='expand("<afile>")')
    def on_bufenter(self, filename):
        buffer_ = self.nvim.current.buffer
        if '/tmp/' not in buffer_.name:
            self.nvim.out_write(
                '{} is a Tweet file but is not stored in the /tmp/ directory \n'.
                format(NeoTwitter.file_name))

    def _trim_buffer(self):
        buffer_content = self.nvim.current.buffer[:]
        # should not exceed CHAR_LENGTH
        tweet = '. '.join(buffer_content)[:NeoTwitter.CHAR_LENGTH]
        return tweet

    def _set_twitter_buffer(self):
        try:
            os.remove(NeoTwitter.file_name.format(NeoTwitter.EXT))
        except FileNotFoundError:
            pass
        self.nvim.command("vs " + NeoTwitter.file_name.format(NeoTwitter.EXT))
        self.nvim.command("set ft={}".format(NeoTwitter.FILETYPE))
