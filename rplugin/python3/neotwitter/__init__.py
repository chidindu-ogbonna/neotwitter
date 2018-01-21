import os

import neovim

from neotwitter.database import Base, engine
from neotwitter.twitter_client import TwitterClient, tweepy
from neotwitter.utils import (get_request_token_from_db, user_in_db,
                              take_screenshot)


@neovim.plugin
class NeoTwitter(object):
    file_path = '/tmp/tweet.twitter'
    VARIABLE = 'neotwitter_verifier'
    CHAR_LENGTH = 140
    COLORSCHEME_MESSAGE = 'Using the "{}" colorscheme. #Neovim #Vim #NeoTwitter'
    FILETYPE = 'twitter'

    def __init__(self, nvim):
        Base.metadata.create_all(engine)

        self.nvim = nvim
        self.twitter_client = TwitterClient()

        self.note_msg = '[NeoTwitter] Note:'
        self.info_msg = '[NeoTwitter] Info:'
        self.error_msg = '[NeoTwitter] Error:'

    def _trim_buffer(self):
        buffer_content = self.nvim.current.buffer[:]
        # should not exceed CHAR_LENGTH
        tweet = '. '.join(buffer_content)[:NeoTwitter.CHAR_LENGTH]
        return tweet

    def _set_twitter_buffer(self):
        try:
            os.remove(NeoTwitter.file_path.format(NeoTwitter.FILETYPE))
        except FileNotFoundError:
            pass
        self.nvim.command(
            "vs " + NeoTwitter.file_path.format(NeoTwitter.FILETYPE))
        self.nvim.command("set ft={}".format(NeoTwitter.FILETYPE))

    def is_verifier_set(self):
        if self.nvim.vars.get(NeoTwitter.VARIABLE):
            return True
        return False

    def get_verifier(self):
        if self.is_verifier_set():
            return self.nvim.vars.get(NeoTwitter.VARIABLE)

    @neovim.command("TwitterStartSetup", sync=True)
    def start_setup(self):
        if self.is_verifier_set() and get_request_token_from_db():
            return self.nvim.out_write(
                '{} Verifier has already been set, run ":TwitterCompleteSetup" to complete setup \n'
            ).format(self.info_msg)
        if self.is_verifier_set() and not get_request_token_from_db():
            return self.nvim.out_write(
                '{} Delete your Verifier and restart the setup \n').format(
                    self.error_msg)
        if not self.is_verifier_set():  # and not get_request_token_from_db():
            try:
                self.twitter_client.get_authorization()
            except tweepy.TweepError as e:
                return self.nvim.out_write('{} {} \n'.format(
                    self.error_msg, e))
            self.nvim.out_write(
                '{} Please check your browser, authorize the application and store your verifier in your vimrc \n'
            ).format(self.info_msg)

    @neovim.command("TwitterCompleteSetup", sync=True)
    def complete_setup(self):
        if user_in_db():
            return self.nvim.out_write(
                '{} A User already in the storage.db, Go on "Tweeting" or x"Delete"x the file if neccessary \n'
            ).self.format(self.info_msg)
        if self.is_verifier_set() and not user_in_db():
            if self.twitter_client.get_tokens(self.get_verifier()):
                self.nvim.out_write('{} Setup was successful \n').self.note_msg
            else:
                self.nvim.out_write(
                    '{} Something went wrong, could not connect to Twitter API \n'
                ).format(self.error_msg)
        else:
            self.nvim.out_write('{} Verifier has not been set \n').format(
                self.error_msg)

    @neovim.command("TweetColorscheme")
    def tweet_colorscheme(self):
        auth = self.twitter_client.build_api()
        colorscheme = self.nvim.vars.get('colors_name')
        message = NeoTwitter.COLORSCHEME_MESSAGE.format(colorscheme)
        try:
            auth.update_with_media(take_screenshot(), status=message)
        except tweepy.TweepError as e:
            self.nvim.out_write('{} {} \n'.format(self.error_msg, e))
            return
        self.nvim.out_write('{} Tweeted colorscheme was "{}" \n'.format(
            self.note_msg, colorscheme))

    @neovim.command("TweetCompose")
    def compose_tweet(self):
        self._set_twitter_buffer()
        self.nvim.out_write(
            '{} If longer than 140 characters, your tweet would be reduced to 140, use "TweetCheckCharacterLength" to check the length \n'
        ).format(self.note_msg)

    @neovim.command("TweetCheckCharacterLength", sync=True)
    def check_length(self):
        buffer_content = self.nvim.current.buffer[:]
        length = len('. '.join(buffer_content))
        self.nvim.out_write('{} Length of Tweet is {} characters \n'.format(
            self.info_msg, length))

    @neovim.command("TweetPost")
    def post_tweet(self):
        buffer_ = self.nvim.current.buffer
        if buffer_.name.split('.')[-1] == NeoTwitter.FILETYPE:
            tweet = self._trim_buffer()
            try:
                auth = self.twitter_client.build_api()
                auth.update_status(tweet)
            except tweepy.TweepError as e:
                return self.nvim.out_write('{} {} \n'.format(
                    self.error_msg, e))
            except Exception as e:
                return self.nvim.out_write('{} {} \n'.format(
                    self.error_msg, e))
            self.nvim.out_write('{} Your tweet was sent \n').format(
                self.info_msg)
        else:
            self.nvim.out_write('{} This is not a tweet file \n').format(
                self.info_msg)

    @neovim.autocmd('BufEnter', pattern='*.twitter', eval='expand("<afile>")')
    def on_bufenter(self, filename):
        buffer_ = self.nvim.current.buffer
        if '/tmp/' not in buffer_.name:
            self.nvim.out_write(
                '{} {} is a Tweet file but does not exist in the proper directory. It will not be posted \n'.
                format(self.note_msg, NeoTwitter.buffer_.name))
