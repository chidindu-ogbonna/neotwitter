from datetime import datetime
import os
from sqlalchemy import Column, DateTime, String, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# The db engine
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(BASE_DIR, 'storage.db'))

# Create the session for sqlalchemy
Session = sessionmaker(bind=engine)
session = Session()

# The Base for the models
Base = declarative_base()


# Models
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    access_token = Column(String(64))
    access_token_secret = Column(String(64))

    def __repr__(self):
        return '<User {}>'.format(self.id)


class Tweets(Base):
    __tablename__ = 'tweetcount'

    id = Column(Integer, primary_key=True)
    tweet_date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Tweet {}>'.format(self.id)
