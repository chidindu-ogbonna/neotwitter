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
    COLORSCHEME_MESSAGE = 'I am using "{}" colorscheme for the week. #Neovim #Vim #NeoTwitter'
    FILETYPE = 'twitter'

    def __init__(self, nvim):
        Base.metadata.create_all(engine)

        self.nvim = nvim
        self.twitter_client = TwitterClient()

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

    def _response_from_get_authorization(self):
        status = self.twitter_client.get_authorization()
        return status

    def _response_from_get_tokens(self, verifier):
        status = self.twitter_client.get_tokens(verifier)
        return status

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
                '[NeoTwitter] Info: Verifier has already been set, run "TwitterCompleteSetup" to continue setup \n'
            )
        if self.is_verifier_set() and not get_request_token_from_db():
            return self.nvim.out_write(
                '[NeoTwitter] Info: Delete your Verifier and restart the setup \n'
            )
        if not self.is_verifier_set():  # and not get_request_token_from_db():
            status = self._response_from_get_authorization()
            if True in status:
                self.nvim.out_write(
                    '[NeoTwitter] Info: Please check your browser and save your "verifier" \n'
                )
            elif False in status:
                self.nvim.out_write('[NeoTwitter] Error: {} \n'.format(
                    status[1]))

    @neovim.command("TwitterCompleteSetup", sync=True)
    def complete_setup(self):
        if user_in_db():
            return self.nvim.out_write(
                '[NeoTwitter] Info: A User already in the storage.db, Delete the file if neccessary \n'
            )
        if self.is_verifier_set() and not user_in_db():
            if self._response_from_get_tokens(self.get_verifier()):
                self.nvim.out_write(
                    '[NeoTwitter] Info: Setup was successful \n')
            else:
                self.nvim.out_write(
                    '[NeoTwitter] Error: Something went wrong, could not connect to Twitter API \n'
                )
        else:
            self.nvim.out_write(
                '[NeoTwitter] Error: Verifier has not been set \n')

    @neovim.command("TweetColorscheme")
    def tweet_colorscheme(self):
        auth = self.twitter_client.build_api()
        colorscheme = self.nvim.vars.get('colors_name')
        message = NeoTwitter.COLORSCHEME_MESSAGE.format(colorscheme)
        try:
            auth.update_with_media(take_screenshot(), status=message)
        except tweepy.TweepError as e:
            self.nvim.out_write('[NeoTwitter] Error: {} \n'.format(e))
            return
        self.nvim.out_write(
            '[NeoTwitter] Info: Tweeted colorscheme was "{}" \n'.format(
                colorscheme))

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
        self.nvim.out_write(
            '[NeoTwitter] Info: Tweet Length is {} \n'.format(length))

    @neovim.command("TweetPost")
    def post_tweet(self):
        buffer_ = self.nvim.current.buffer
        if buffer_.name.split('.')[-1] == NeoTwitter.FILETYPE:
            tweet = self._trim_buffer()
            try:
                auth = self.twitter_client.build_api()
                auth.update_status(tweet)
            except tweepy.TweepError as e:
                self.nvim.out_write('[NeoTwitter] Error: {} \n'.format(e))
            except Exception as e:
                self.nvim.out_write('[NeoTwitter] Error: {} \n'.format(e))
            self.nvim.out_write('[NeoTwitter] Info: Your tweet was sent \n')
        else:
            self.nvim.out_write(
                '[NeoTwitter] Info: This is not a tweet file \n')

    @neovim.autocmd('BufEnter', pattern='*.twitter', eval='expand("<afile>")')
    def on_bufenter(self, filename):
        buffer_ = self.nvim.current.buffer
        if '/tmp/' not in buffer_.name:
            self.nvim.out_write(
                '[NeoTwitter] Note: {} is a Tweet file but does not exist in the proper directory. It will not be posted \n'.
                format(NeoTwitter.buffer_.name))
