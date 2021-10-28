import os

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime
)

from sqlalchemy import orm
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import relationship
import sys

engine = create_engine("mysql+pymysql://root:12272027@127.0.0.1:3306/mydb")
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
BaseModel = declarative_base()

class User(BaseModel):
    __tablename__ = "user"
    userId = Column(Integer, primary_key=True)
    username = Column(String(45))
    firstName = Column(String(45))
    lastName = Column(String(45))
    email = Column(String(45))
    password = Column(String(45))
    phone = Column(Integer)
    reservation = relationship('Reserve')
    def __str__(self):
        return f"User ID        :{self.userId}\n"\
               f"Username       :{self.username}\n" \
               f"First name     :{self.firstName}\n" \
               f"Last name      :{self.lastName}\n" \
               f"Email          :{self.email}\n" \
               f"Password       :{self.password}\n" \
               f"Phone          :{self.phone}\n"


class Audience(BaseModel):
    __tablename__ = "audience"
    audienceId = Column(Integer, primary_key=True)
    name = Column(String(45))
    audience = relationship('Reserve', uselist = False)

    def __str__(self):
        return f"Audience ID        :{self.audienceId}\n"\
               f"Audience           :{self.name}\n"


class Reserve(BaseModel):
    __tablename__ = "reserve"
    reserveId = Column(Integer, primary_key=True)
    begin = Column(DateTime)
    end = Column(DateTime)
    userId = Column(Integer, ForeignKey('user.userId'))
    audienceId = Column(Integer, ForeignKey('audience.audienceId'))


    def __str__(self):
        return f"Reserve ID          :{self.reserveId}\n"\
               f"Begin               :{self.begin}\n" \
               f"End                 :{self.end}\n" \
               f"User ID             :{self.userId}\n" \
               f"Audience ID         :{self.audienceId}\n"