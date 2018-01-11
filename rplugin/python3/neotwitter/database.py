import os

from sqlalchemy import Column, Integer, PickleType, String, create_engine
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
    request_token = Column(PickleType)

    def __repr__(self):
        return '<User {}>'.format(self.id)
